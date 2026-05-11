from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.REST.data.database import get_db
from app.REST.model.product_schema import Product, ProductCreate, ProductHistoryEntry
from app.REST.service.product_service import (
    list_products,
    get_product,
    create_product,
    replace_product,
    remove_product,
    list_product_history,
)
from app.REST.service.product_validators import ValidationError, ConflictError, ResourceNotFoundError

router = APIRouter(tags=["Products"])


@router.get("/products", response_model=list[Product])
def api_get_products(db: Session = Depends(get_db)):
    return list_products(db)


@router.get("/products/{id}", response_model=Product)
def api_get_product(id: int, db: Session = Depends(get_db)):
    product = get_product(db, id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/products", response_model=Product, status_code=201)
def post_product(payload: ProductCreate, db: Session = Depends(get_db)):
    try:
        return create_product(db, payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/products/{id}", response_model=Product)
def put_product(id: int, payload: ProductCreate, db: Session = Depends(get_db)):
    try:
        product = replace_product(db, id, payload)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/products/{id}", status_code=204)
def delete_product_endpoint(id: int, db: Session = Depends(get_db)):
    if not remove_product(db, id):
        raise HTTPException(status_code=404, detail="Product not found")
    return Response(status_code=204)


@router.get("/products/{id}/history", response_model=list[ProductHistoryEntry])
def get_product_history_endpoint(id: int, db: Session = Depends(get_db)):
    return list_product_history(db, id)