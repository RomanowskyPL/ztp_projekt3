from sqlalchemy import Column, Integer, String, ForeignKey, Numeric

from app.REST.data.database import Base


class OrderItemORM(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)

    product_id = Column(Integer, nullable=False)
    product_name = Column(String, nullable=False)
    product_price = Column(Numeric(10, 2), nullable=False)

    quantity = Column(Integer, nullable=False)
    line_total = Column(Numeric(10, 2), nullable=False)