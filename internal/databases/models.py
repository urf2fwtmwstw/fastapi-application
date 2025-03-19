import enum
import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import  DeclarativeBase, relationship
from sqlalchemy import Column, ForeignKey, Enum, Numeric, String, DateTime


class Base(DeclarativeBase):
    pass

class CategoryTypes(enum.Enum):
    income = "income"
    expenses = "expenses"

class TransactionTypes(enum.Enum):
    income = "income"
    expenses = "expenses"

# class User(Base):
#     __tablename__ = "users"
#     user_id = Column(UUID(as_uuid=True), primary_key=True)

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(UUID(as_uuid=True), primary_key=True)
    category_name = Column(String(50), nullable=False, unique=True)
    category_description = Column(String(200), nullable=False)
    category_type = Column(Enum(CategoryTypes), nullable=False)
    # user_id = Column(ForeignKey("users.user_id"))


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(UUID(as_uuid=True), primary_key=True)
    transaction_type = Column(Enum(TransactionTypes), nullable=False)
    transaction_value = Column(Numeric(precision=10, scale=2), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    transaction_created = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)
    transaction_description = Column(String(200))
    #user_id = Column(ForeignKey("users.user_id"))
    category_id = Column(ForeignKey("categories.category_id"))
