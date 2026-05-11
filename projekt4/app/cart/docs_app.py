from fastapi import FastAPI
from app.cart.web.routes import router

cart_docs_app = FastAPI(
    title="Cart API",
    docs_url="/",
    openapi_url="/openapi.json",
)

cart_docs_app.include_router(router, prefix="/api/v1")