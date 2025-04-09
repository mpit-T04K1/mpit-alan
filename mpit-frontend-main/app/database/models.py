from enum import Enum

# from sqlalchemy import 
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class BusinessType(Enum):
    cafe=1
    restaurant=2
    bar=3
    shop=4
    other=5


class Base(DeclarativeBase):
    pass

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    business_type: Mapped[BusinessType]
    address: Mapped[str]
    phone: Mapped[str]
    email: Mapped[str]
    description: Mapped[str] = mapped_column(nullable=True)
    logo: Mapped[str]
