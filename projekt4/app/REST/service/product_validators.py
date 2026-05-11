import re
from sqlalchemy.orm import Session
from app.REST.data.product_repository import get_product_by_name, get_category_by_id, get_forbidden_name

class ValidationError(Exception):
    pass

class ConflictError(Exception):
    pass

class ResourceNotFoundError(Exception):
    pass

def validate_product(db: Session, name: str, price: float, quantity: int, category_id: int, product_id: int | None = None):
    if not (3 <= len(name) <= 20):
        raise ValidationError("Nazwa musi mieć od 3 do 20 znaków.")
    if not re.fullmatch(r"[A-Za-z0-9]+", name):
        raise ValidationError("Nazwa może zawierać tylko litery i cyfry.")
    existing = get_product_by_name(db, name)
    if existing is not None and existing.id != product_id:
        raise ConflictError("Produkt o takiej nazwie już istnieje.")
    forbidden = get_forbidden_name(db, name)
    if forbidden is not None:
        raise ValidationError("Ta nazwa jest zakazana.")
    if quantity < 0:
        raise ValidationError("Ilość sztuk nie może być mniejsza od 0.")
    category = get_category_by_id(db, category_id)
    if category is None:
        raise ResourceNotFoundError("Kategoria nie istnieje.")
    if price < float(category.min_price) or price > float(category.max_price):
        raise ValidationError("Cena nie mieści się w widełkach kategorii.")