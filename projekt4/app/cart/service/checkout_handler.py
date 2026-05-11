from sqlalchemy.orm import Session

from app.cart.service.checkout_command import CheckoutCommand
from app.cart.service.cart_service import checkout
from app.cart.model.cart_schema import OrderResponse


def handle_checkout(db: Session, command: CheckoutCommand) -> OrderResponse:
    return checkout(db, command.operator_id)