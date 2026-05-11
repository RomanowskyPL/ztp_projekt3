from fastapi import FastAPI

from app.REST.web.routes import router as products_router

products_docs_app = FastAPI(
    title="Products API",
    docs_url="/",
    redoc_url=None,
    openapi_url="/openapi.json",
)

products_docs_app.include_router(products_router, prefix="/api/v1")