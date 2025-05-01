import datetime
import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class CategoryType(enum.Enum):
    income = "income"
    expenses = "expenses"


class TransactionType(enum.Enum):
    income = "income"
    expenses = "expenses"


class ReportStatus(enum.Enum):
    created = "CREATED"
    generated = "GENERATED"
    failed = "FAILED"


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(UUID(as_uuid=True), primary_key=True)
    category_name = Column(String(50), nullable=False)
    category_description = Column(String(200), nullable=False)
    category_type = Column(Enum(CategoryType), nullable=False)
    user_id = Column(ForeignKey("users.user_id"))


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(UUID(as_uuid=True), primary_key=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    transaction_value = Column(Numeric(precision=10, scale=2), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    transaction_created = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.datetime.now,
    )
    transaction_description = Column(String(200))
    user_id = Column(ForeignKey("users.user_id"))
    category_id = Column(ForeignKey("categories.category_id"))


class Report(Base):
    __tablename__ = "reports"

    report_id = Column(UUID(as_uuid=True), primary_key=True)
    report_created = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.datetime.now,
    )
    report_year_month = Column(String(7), nullable=False)
    month_income = Column(Numeric(precision=10, scale=2))
    month_expenses = Column(Numeric(precision=10, scale=2))
    balance = Column(Numeric(precision=10, scale=2))
    most_expensive_categories = Column(String(188))
    user_id = Column(ForeignKey("users.user_id"), nullable=False)
    status = Column(
        Enum(
            ReportStatus,
            values_callable=lambda statuses: [str(status.value) for status in statuses],
        ),
        nullable=False,
    )
