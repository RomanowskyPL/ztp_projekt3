from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import relationship

from app.REST.data.database import Base


class OrderORM(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id", ondelete="CASCADE"), nullable=False)

    order_number = Column(String, nullable=False, unique=True)
    status = Column(String, nullable=False, default="PENDING")
    total_price = Column(Numeric(10, 2), nullable=False, default=0)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    items = relationship(
        "OrderItemORM",
        cascade="all, delete-orphan",
        lazy="selectin",
    )