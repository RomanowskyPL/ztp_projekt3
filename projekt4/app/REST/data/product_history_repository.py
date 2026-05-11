from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from app.REST.model.product_history_orm import ProductHistoryORM


def add_product_history(db: Session, entry: ProductHistoryORM):
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_product_history(db: Session, product_id: int):
    query = (
        select(ProductHistoryORM)
        .where(ProductHistoryORM.product_id == product_id)
        .order_by(desc(ProductHistoryORM.changed_at), desc(ProductHistoryORM.id))
    )
    return db.execute(query).scalars().all()