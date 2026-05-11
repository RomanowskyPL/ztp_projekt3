from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.REST.data.database import Base, engine
from app.REST.model.product_orm import ProductORM, CategoryORM, ForbiddenProductNameORM

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.REST.model.product_orm import ProductORM

def create_tables():
    Base.metadata.create_all(engine)

def seed_if_empty(db: Session):
    exists = db.execute(select(CategoryORM).limit(1)).scalars().first()
    if exists:
        return

    cat1 = CategoryORM(name="Elektronika", min_price=50.0, max_price=5000.0)
    cat2 = CategoryORM(name="Spozywcze", min_price=1.0, max_price=100.0)

    db.add_all([cat1, cat2])
    db.flush()

    db.add_all([
        ForbiddenProductNameORM(name="Admin"),
        ForbiddenProductNameORM(name="Test"),
    ])

    db.add_all([
        ProductORM(name="Sluchawki", price=299.99, quantity=10, category_id=cat1.id),
        ProductORM(name="Chleb", price=4.99, quantity=20, category_id=cat2.id),
    ])

    db.commit()

def get_all_products(db: Session):
    query = select(ProductORM).options(joinedload(ProductORM.category))
    return db.execute(query).scalars().all()

def get_product_by_id(db: Session, product_id: int):
    query = (
        select(ProductORM)
        .where(ProductORM.id == product_id)
        .options(joinedload(ProductORM.category))
    )
    return db.execute(query).scalars().first()

def get_product_by_name(db: Session, name: str):
    query = select(ProductORM).where(ProductORM.name == name)
    return db.execute(query).scalars().first()

def get_category_by_id(db: Session, category_id: int):
    query = select(CategoryORM).where(CategoryORM.id == category_id)
    return db.execute(query).scalars().first()

def get_forbidden_name(db: Session, name: str):
    query = select(ForbiddenProductNameORM).where(ForbiddenProductNameORM.name == name)
    return db.execute(query).scalars().first()

def add_product(db: Session, product: ProductORM):
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def save_product(db: Session, product: ProductORM):
    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product: ProductORM):
    db.delete(product)
    db.commit()

def get_product_or_none(db: Session, product_id: int):
    query = select(ProductORM).where(ProductORM.id == product_id)
    return db.execute(query).scalars().first()


def update_product_quantity(db: Session, product: ProductORM, new_quantity: int):
    product.quantity = new_quantity
    db.commit()
    db.refresh(product)
    return product