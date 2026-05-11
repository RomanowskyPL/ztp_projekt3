from decimal import Decimal
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.REST.data.product_repository import get_product_or_none
from app.cart.data.cart_repository import (
    get_or_create_cart,
    add_item_to_cart,
    get_cart_item,
    delete_cart_item,
    update_cart_item_quantity,
    clear_cart,
    create_order,
    list_orders,
    get_order,
)
from app.cart.model.order_item_orm import OrderItemORM
from app.cart.model.cart_schema import (
    CartResponse,
    CartItemResponse,
    OrderResponse,
    OrderItemResponse,
    OrderListItemResponse,
)


def _cart_total(cart) -> Decimal:
    total = Decimal("0.00")
    for item in cart.items:
        total += Decimal(item.product.price) * item.quantity
    return total


def _build_cart_response(cart) -> CartResponse:
    items = []
    for item in cart.items:
        price = Decimal(item.product.price)
        line_total = price * item.quantity

        items.append(
            CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name,
                product_price=price,
                quantity=item.quantity,
                line_total=line_total,
            )
        )

    return CartResponse(
        id=cart.id,
        operator_id=cart.operator_id,
        items=items,
        total_price=_cart_total(cart),
    )


def get_cart(db: Session, operator_id: int) -> CartResponse:
    cart = get_or_create_cart(db, operator_id)
    db.refresh(cart)
    return _build_cart_response(cart)


def add_to_cart(db: Session, operator_id: int, product_id: int, quantity: int) -> CartResponse:
    cart = get_or_create_cart(db, operator_id)

    product = get_product_or_none(db, product_id)
    if not product:
        raise LookupError("Produkt nie istnieje.")

    if quantity <= 0:
        raise ValueError("Ilość musi być większa od 0.")

    if quantity > product.quantity:
        raise ValueError("Brak wystarczającej ilości produktu w magazynie.")

    try:
        add_item_to_cart(db, cart.id, product_id, quantity)
    except IntegrityError:
        raise ValueError("Ten produkt już istnieje w koszyku (użyj PATCH).")

    db.refresh(cart)
    return _build_cart_response(cart)


def update_cart_item(db: Session, operator_id: int, item_id: int, quantity: int) -> CartResponse:
    cart = get_or_create_cart(db, operator_id)
    item = get_cart_item(db, item_id)

    if not item or item.cart_id != cart.id:
        raise LookupError("Nie znaleziono pozycji koszyka.")

    if quantity <= 0:
        raise ValueError("Ilość musi być większa od 0.")

    product = get_product_or_none(db, item.product_id)
    if not product:
        raise ValueError("Produkt nie istnieje.")

    if quantity > product.quantity:
        raise ValueError("Brak wystarczającej ilości produktu w magazynie.")

    update_cart_item_quantity(db, item, quantity)

    db.refresh(cart)
    return _build_cart_response(cart)


def remove_cart_item(db: Session, operator_id: int, item_id: int) -> CartResponse:
    cart = get_or_create_cart(db, operator_id)
    item = get_cart_item(db, item_id)

    if not item or item.cart_id != cart.id:
        raise LookupError("Nie znaleziono pozycji koszyka.")

    delete_cart_item(db, item_id)

    db.refresh(cart)
    return _build_cart_response(cart)


def _generate_order_number(order_id: int) -> str:
    today = datetime.now().strftime("%Y%m%d")
    return f"ZAM-{today}-{order_id:06d}"


def checkout(db: Session, operator_id: int) -> OrderResponse:
    cart = get_or_create_cart(db, operator_id)

    if not cart.items:
        raise ValueError("Koszyk jest pusty.")

    order = create_order(db, operator_id)
    order.order_number = _generate_order_number(order.id)

    total_price = Decimal("0.00")

    for item in cart.items:
        product = get_product_or_none(db, item.product_id)
        if not product:
            raise ValueError("Produkt nie istnieje.")

        if item.quantity > product.quantity:
            raise ValueError(f"Brak produktu {product.name} w magazynie.")

        price = Decimal(product.price)
        line_total = price * item.quantity
        total_price += line_total

        order_item = OrderItemORM(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            product_price=price,
            quantity=item.quantity,
            line_total=line_total,
        )
        db.add(order_item)

        product.quantity -= item.quantity
        db.add(product)

    order.total_price = total_price
    db.add(order)
    db.commit()
    db.refresh(order)

    clear_cart(db, cart.id)

    return get_order_details(db, operator_id, order.id)


def get_orders(db: Session, operator_id: int) -> list[OrderListItemResponse]:
    orders = list_orders(db, operator_id)
    return [
        OrderListItemResponse(
            id=o.id,
            order_number=o.order_number,
            status=o.status,
            total_price=o.total_price,
            created_at=o.created_at,
        )
        for o in orders
    ]


def get_order_details(db: Session, operator_id: int, order_id: int) -> OrderResponse:
    order = get_order(db, order_id, operator_id)
    if not order:
        raise LookupError("Nie znaleziono zamówienia.")

    items = [
        OrderItemResponse(
            id=i.id,
            product_id=i.product_id,
            product_name=i.product_name,
            product_price=i.product_price,
            quantity=i.quantity,
            line_total=i.line_total,
        )
        for i in order.items
    ]

    return OrderResponse(
        id=order.id,
        operator_id=order.operator_id,
        order_number=order.order_number,
        status=order.status,
        total_price=order.total_price,
        created_at=order.created_at,
        items=items,
    )


def remove_from_cart(db: Session, operator_id: int, product_id: int):
    cart = get_or_create_cart(db, operator_id)
    item = next((i for i in cart.items if i.product_id == product_id), None)

    if not item:
        raise LookupError("Nie znaleziono produktu w koszyku.")

    return remove_cart_item(db, operator_id, item.id)


def checkout_cart(db: Session, operator_id: int):
    order = checkout(db, operator_id)
    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "total_price": float(order.total_price),
    }