from sqlalchemy import Integer, Text, String, Float, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


Good_price = CheckConstraint('price >= 0', name='price_constraint')


class Base(DeclarativeBase):
    # def __repr__(self):
    #     return f"{self.__name__} - Ruslanchik"
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[bytes] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    image_path = mapped_column(Text, default='img.png')


class Pizza(Base):
    __tablename__ = 'pizzas'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        Good_price,
    )


class Beverage(Base):
    __tablename__ = 'beverages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        Good_price,
    )
