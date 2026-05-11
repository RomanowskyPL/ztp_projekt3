from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.REST.data.database import get_db
from app.identity.service.auth_service import get_current_operator

from app.cart.model.cart_schema import CartResponse, AddToCartRequest, CheckoutResponse
from app.cart.service.cart_service import get_cart, add_to_cart, remove_from_cart, checkout_cart

router = APIRouter(tags=["Cart"])


@router.get("/cart", response_model=CartResponse, status_code=status.HTTP_200_OK)
def get_cart_endpoint(
    db: Session = Depends(get_db),
    operator=Depends(get_current_operator),
):
    return get_cart(db, operator.id)


@router.post("/cart/items", response_model=CartResponse, status_code=status.HTTP_200_OK)
def add_to_cart_endpoint(
    payload: AddToCartRequest,
    db: Session = Depends(get_db),
    operator=Depends(get_current_operator),
):
    try:
        return add_to_cart(db, operator.id, payload.product_id, payload.quantity)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/cart/items/{product_id}", response_model=CartResponse, status_code=status.HTTP_200_OK)
def remove_from_cart_endpoint(
    product_id: int,
    db: Session = Depends(get_db),
    operator=Depends(get_current_operator),
):
    try:
        return remove_from_cart(db, operator.id, product_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/cart/checkout", response_model=CheckoutResponse, status_code=status.HTTP_200_OK)
def checkout_endpoint(
    db: Session = Depends(get_db),
    operator=Depends(get_current_operator),
):
    try:
        return checkout_cart(db, operator.id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))