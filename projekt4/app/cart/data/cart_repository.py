from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.cart.model.cart_orm import CartORM
from app.cart.model.cart_item_orm import CartItemORM
from app.cart.model.order_orm import OrderORM
from app.cart.model.order_item_orm import OrderItemORM


def get_cart_by_operator_id(db: Session, operator_id: int):
    return db.query(CartORM).filter(CartORM.operator_id == operator_id).first()


def create_cart(db: Session, operator_id: int):
    cart = CartORM(operator_id=operator_id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart


def get_or_create_cart(db: Session, operator_id: int):
    cart = get_cart_by_operator_id(db, operator_id)
    if cart:
        return cart
    return create_cart(db, operator_id)


def add_item_to_cart(db: Session, cart_id: int, product_id: int, quantity: int):
    item = CartItemORM(cart_id=cart_id, product_id=product_id, quantity=quantity)
    db.add(item)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    db.refresh(item)
    return item


def get_cart_item(db: Session, item_id: int):
    return db.query(CartItemORM).filter(CartItemORM.id == item_id).first()


def delete_cart_item(db: Session, item_id: int):
    item = get_cart_item(db, item_id)
    if not item:
        return None

    db.delete(item)
    db.commit()
    return item


def update_cart_item_quantity(db: Session, item: CartItemORM, quantity: int):
    item.quantity = quantity
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def clear_cart(db: Session, cart_id: int):
    db.query(CartItemORM).filter(CartItemORM.cart_id == cart_id).delete()
    db.commit()


def create_order(db: Session, operator_id: int):
    order = OrderORM(operator_id=operator_id, order_number="TEMP")
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def add_order_item(db: Session, order_item: OrderItemORM):
    db.add(order_item)
    db.commit()
    db.refresh(order_item)
    return order_item


def list_orders(db: Session, operator_id: int):
    return db.query(OrderORM).filter(OrderORM.operator_id == operator_id).order_by(OrderORM.created_at.desc()).all()


def get_order(db: Session, order_id: int, operator_id: int):
    return db.query(OrderORM).filter(OrderORM.id == order_id, OrderORM.operator_id == operator_id).first()