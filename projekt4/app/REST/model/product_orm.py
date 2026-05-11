from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Numeric, ForeignKey
from app.REST.data.database import Base


class CategoryORM(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    min_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    max_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    products: Mapped[list["ProductORM"]] = relationship(back_populates="category")


class ForbiddenProductNameORM(Base):
    __tablename__ = "forbidden_product_names"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)


class ProductORM(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category: Mapped[CategoryORM] = relationship(back_populates="products")