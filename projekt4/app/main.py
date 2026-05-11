from fastapi import FastAPI
from threading import Thread
from contextlib import asynccontextmanager

from app.REST.web.routes import router as products_router
from app.notifications.web.routes import router as notifications_router
from app.REST.docs_app import products_docs_app
from app.notifications.docs_app import notifications_docs_app
from app.notifications.service.notification_worker import run_worker

from app.REST.data.product_repository import create_tables, seed_if_empty
from app.REST.data.database import SessionLocal

from app.notifications.model.notification_orm import NotificationORM  # noqa: F401
from app.identity.web.routes import router as identity_router
from app.identity.docs_app import identity_docs_app
from app.identity.model.operator_orm import OperatorORM  # noqa: F401
from app.identity.model.operator_session_orm import OperatorSessionORM  # noqa: F401

from app.cart.web.routes import router as cart_router
from app.cart.docs_app import cart_docs_app

from app.cart.model.cart_orm import CartORM  # noqa: F401
from app.cart.model.cart_item_orm import CartItemORM  # noqa: F401
from app.cart.model.order_orm import OrderORM  # noqa: F401
from app.cart.model.order_item_orm import OrderItemORM  # noqa: F401

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()

    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()

    thread = Thread(target=run_worker, daemon=True)
    thread.start()

    yield


app = FastAPI(
    title="Laboratorium 6 - Notifications",
    lifespan=lifespan,
)

app.include_router(products_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(identity_router, prefix="/api/v1")

app.mount("/student-docs", products_docs_app)
app.mount("/notifications-docs", notifications_docs_app)
app.mount("/identity-docs", identity_docs_app)

app.include_router(cart_router, prefix="/api/v1")
app.mount("/cart-docs", cart_docs_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)