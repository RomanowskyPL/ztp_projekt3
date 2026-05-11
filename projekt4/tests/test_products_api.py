def build_product_payload(name: str) -> dict:
    return {
        "name": name,
        "price": 999.99,
        "quantity": 5,
        "category_id": 1,
    }


def test_get_products_returns_200_and_non_empty_list(client):
    response = client.get("/api/v1/products")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    first = data[0]
    assert "id" in first
    assert "name" in first
    assert "price" in first
    assert "quantity" in first
    assert "category" in first


def test_post_products_creates_product_and_history_entry(client, unique_product_name):
    payload = build_product_payload(unique_product_name)

    create_response = client.post("/api/v1/products", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()

    assert created["name"] == payload["name"]
    assert created["price"] == payload["price"]
    assert created["quantity"] == payload["quantity"]
    assert created["category"]["id"] == payload["category_id"]

    product_id = created["id"]

    history_response = client.get(f"/api/v1/products/{product_id}/history")
    assert history_response.status_code == 200

    history = history_response.json()
    assert isinstance(history, list)
    assert len(history) >= 1

    latest_entry = history[0]
    assert latest_entry["product_id"] == product_id
    assert latest_entry["action"] == "CREATE"
    assert latest_entry["previous_state"] == {}
    assert latest_entry["current_state"]["name"] == payload["name"]
    assert latest_entry["current_state"]["price"] == payload["price"]
    assert latest_entry["current_state"]["quantity"] == payload["quantity"]


def test_put_products_updates_product_and_saves_history(client, unique_product_name):
    create_payload = build_product_payload(unique_product_name)
    create_response = client.post("/api/v1/products", json=create_payload)
    assert create_response.status_code == 201

    created_product = create_response.json()
    product_id = created_product["id"]

    update_payload = {
        "name": unique_product_name + "X",
        "price": 1200.00,
        "quantity": 8,
        "category_id": 1,
    }

    put_response = client.put(f"/api/v1/products/{product_id}", json=update_payload)

    assert put_response.status_code == 200
    updated = put_response.json()

    assert updated["id"] == product_id
    assert updated["name"] == update_payload["name"]
    assert updated["price"] == update_payload["price"]
    assert updated["quantity"] == update_payload["quantity"]

    history_response = client.get(f"/api/v1/products/{product_id}/history")
    assert history_response.status_code == 200

    history = history_response.json()
    assert len(history) >= 2

    latest_entry = history[0]
    create_entry = history[1]

    assert latest_entry["action"] == "REPLACE"
    assert latest_entry["previous_state"]["name"] == create_payload["name"]
    assert latest_entry["current_state"]["name"] == update_payload["name"]
    assert latest_entry["previous_state"]["price"] == create_payload["price"]
    assert latest_entry["current_state"]["price"] == update_payload["price"]
    assert latest_entry["previous_state"]["quantity"] == create_payload["quantity"]
    assert latest_entry["current_state"]["quantity"] == update_payload["quantity"]

    assert create_entry["action"] == "CREATE"


def test_post_products_rejects_name_with_invalid_length(client):
    payload = {
        "name": "AB",
        "price": 999.99,
        "quantity": 5,
        "category_id": 1,
    }

    response = client.post("/api/v1/products", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "Nazwa musi mieć od 3 do 20 znaków."


def test_post_products_rejects_negative_quantity(client, unique_product_name):
    payload = build_product_payload(unique_product_name)
    payload["quantity"] = -1

    response = client.post("/api/v1/products", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "Ilość sztuk nie może być mniejsza od 0."


def test_post_products_rejects_price_out_of_category_range(client, unique_product_name):
    payload = build_product_payload(unique_product_name)
    payload["price"] = 10.00

    response = client.post("/api/v1/products", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "Cena nie mieści się w widełkach kategorii."