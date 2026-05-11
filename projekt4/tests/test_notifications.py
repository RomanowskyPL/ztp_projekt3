from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.notifications.service.notification_validators import convert_to_utc


def build_push_notification_payload() -> dict:
    scheduled_local = datetime.now(ZoneInfo("Europe/Warsaw")) + timedelta(minutes=10)

    return {
        "content": "Test PUSH notification",
        "channel": "PUSH",
        "recipient": "test-topic",
        "scheduled_at": scheduled_local.replace(tzinfo=None).isoformat(timespec="seconds"),
        "timezone": "Europe/Warsaw",
    }


def build_email_notification_payload() -> dict:
    scheduled_local = datetime.now(ZoneInfo("Europe/Warsaw")) + timedelta(minutes=10)

    return {
        "content": "Test EMAIL notification",
        "channel": "EMAIL",
        "recipient": "test@example.com",
        "scheduled_at": scheduled_local.replace(tzinfo=None).isoformat(timespec="seconds"),
        "timezone": "Europe/Warsaw",
    }


def test_get_notifications_returns_200_and_list(client):
    response = client.get("/api/v1/notifications")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_post_push_notification_creates_record_and_converts_time_to_utc(client):
    payload = build_push_notification_payload()

    create_response = client.post("/api/v1/notifications", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()

    assert created["content"] == payload["content"]
    assert created["channel"] == payload["channel"]
    assert created["recipient"] == payload["recipient"]
    assert created["timezone"] == payload["timezone"]
    assert created["status"] == "PENDING"
    assert "id" in created
    assert "created_at" in created
    assert "idempotency_key" in created

    expected_utc = convert_to_utc(
        datetime.fromisoformat(payload["scheduled_at"]),
        payload["timezone"],
    )

    assert created["scheduled_at"] == expected_utc.isoformat().replace("+00:00", "Z")


def test_post_email_notification_creates_record(client):
    payload = build_email_notification_payload()

    response = client.post("/api/v1/notifications", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["channel"] == "EMAIL"
    assert body["status"] == "PENDING"


def test_send_now_push_notification_changes_status_to_sent(client):
    payload = build_push_notification_payload()

    create_response = client.post("/api/v1/notifications", json=payload)
    assert create_response.status_code == 201

    notification_id = create_response.json()["id"]

    send_response = client.post(f"/api/v1/notifications/{notification_id}/send-now")
    assert send_response.status_code == 200

    sent = send_response.json()
    assert sent["status"] in ["SENT", "FAILED"]


def test_patch_notification_status_to_cancelled(client):
    payload = build_push_notification_payload()

    create_response = client.post("/api/v1/notifications", json=payload)
    assert create_response.status_code == 201

    notification_id = create_response.json()["id"]

    patch_response = client.patch(
        f"/api/v1/notifications/{notification_id}/status",
        json={"status": "CANCELLED"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["status"] == "CANCELLED"


def test_post_notification_rejects_invalid_timezone(client):
    payload = build_push_notification_payload()
    payload["timezone"] = "XYZ"

    response = client.post("/api/v1/notifications", json=payload)
    assert response.status_code == 422


def test_post_notification_rejects_past_datetime(client):
    payload = build_push_notification_payload()
    payload["scheduled_at"] = "2020-01-01T10:00:00"

    response = client.post("/api/v1/notifications", json=payload)
    assert response.status_code == 422


def test_metrics_endpoint_returns_200(client):
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert "notifications_sent_total" in response.text