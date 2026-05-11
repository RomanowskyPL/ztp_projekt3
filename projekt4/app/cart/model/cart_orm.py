from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.REST.data.database import Base


class CartORM(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    items = relationship(
        "CartItemORM",
        cascade="all, delete-orphan",
        lazy="selectin",
    )