from sqlalchemy.orm import Session
from app.REST.data.product_repository import (
    get_all_products,
    get_product_by_id,
    add_product,
    save_product,
    delete_product,
)
from app.REST.model.product_orm import ProductORM
from app.REST.model.product_schema import ProductCreate
from app.REST.service.product_validators import validate_product
from app.REST.data.product_history_repository import add_product_history, get_product_history
from app.REST.model.product_history_orm import ProductHistoryORM

def list_products(db: Session):
    return get_all_products(db)

def get_product(db: Session, product_id: int):
    return get_product_by_id(db, product_id)

def create_product(db: Session, payload: ProductCreate):
    validate_product(db, payload.name, payload.price, payload.quantity, payload.category_id)

    product = ProductORM(
        name=payload.name,
        price=payload.price,
        quantity=payload.quantity,
        category_id=payload.category_id,
    )
    created = add_product(db, product)
    created = get_product_by_id(db, created.id)

    _save_product_history(
        db=db,
        product_id=created.id,
        action="CREATE",
        previous_state={},
        current_state=_build_product_snapshot(created),
    )

    return created

def replace_product(db: Session, product_id: int, payload: ProductCreate):
    product = get_product_by_id(db, product_id)
    if product is None:
        return None

    previous_state = _build_product_snapshot(product)

    validate_product(db, payload.name, payload.price, payload.quantity, payload.category_id, product_id)

    product.name = payload.name
    product.price = payload.price
    product.quantity = payload.quantity
    product.category_id = payload.category_id

    updated = save_product(db, product)
    updated = get_product_by_id(db, updated.id)

    _save_product_history(
        db=db,
        product_id=updated.id,
        action="REPLACE",
        previous_state=previous_state,
        current_state=_build_product_snapshot(updated),
    )

    return updated

def remove_product(db: Session, product_id: int):
    product = get_product_by_id(db, product_id)
    if product is None:
        return False

    previous_state = _build_product_snapshot(product)
    current_id = product.id

    delete_product(db, product)

    _save_product_history(
        db=db,
        product_id=current_id,
        action="DELETE",
        previous_state=previous_state,
        current_state={},
    )

    return True

def _build_product_snapshot(product):
    return {
        "id": product.id,
        "name": product.name,
        "price": float(product.price),
        "quantity": product.quantity,
        "category": {
            "id": product.category.id,
            "name": product.category.name,
        },
    }

def _save_product_history(db: Session, product_id: int, action: str, previous_state: dict, current_state: dict):
    entry = ProductHistoryORM(
        product_id=product_id,
        action=action,
        previous_state=previous_state,
        current_state=current_state,
    )
    return add_product_history(db, entry)


def list_product_history(db: Session, product_id: int):
    return get_product_history(db, product_id)