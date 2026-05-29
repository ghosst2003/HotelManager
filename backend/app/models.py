from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime,
    DECIMAL, ForeignKey, func, SmallInteger
)
from sqlalchemy.orm import relationship
from app.database import Base


class TimestampMixin:
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, default="employee")
    display_name = Column(String(100), nullable=False)
    is_active = Column(SmallInteger, nullable=False, default=1)


class Order(TimestampMixin, Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_platform = Column(String(50), nullable=False)
    order_number = Column(String(100), nullable=False)
    room_name = Column(String(200), nullable=False)
    guest_name = Column(String(100), nullable=False)
    salesperson = Column(String(100), nullable=False)
    hotel_name = Column(String(200), nullable=False)
    guest_count = Column(Integer, nullable=False, default=1)
    booking_date = Column(Date, nullable=False)
    confirmation_number = Column(String(100), nullable=True)
    order_status = Column(String(30), nullable=False, default="未处理")
    other_remarks = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_deleted = Column(SmallInteger, nullable=False, default=0)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    deleter = relationship("User", foreign_keys=[deleted_by])


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    date = Column(Date, nullable=False)
    room_count = Column(Integer, nullable=False)
    cost_price = Column(DECIMAL(10, 2), nullable=False)
    sale_price = Column(DECIMAL(10, 2), nullable=False)
    gross_profit = Column(
        DECIMAL(10, 2),
        nullable=False,
        default=0,
        comment="Auto-calculated: sale_price - cost_price + sum(additional_expenses.profit)",
    )
    profit_margin = Column(
        DECIMAL(5, 2),
        nullable=False,
        default=0,
        comment="Auto-calculated: gross_profit / sale_price * 100",
    )
    salesperson = Column(String(100), nullable=True)
    confirmation_number = Column(String(100), nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    order = relationship("Order", back_populates="items")
    additional_expenses = relationship("AdditionalExpense", back_populates="order_item", cascade="all, delete-orphan")


class AdditionalExpense(Base):
    __tablename__ = "additional_expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False)
    item = Column(String(255), nullable=False, default="")
    cost = Column(DECIMAL(10, 2), nullable=False, default=0)
    expense = Column(DECIMAL(10, 2), nullable=False, default=0)
    profit = Column(DECIMAL(10, 2), nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    order_item = relationship("OrderItem", back_populates="additional_expenses")


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(
        String(50),
        nullable=False,
    )
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    user = relationship("User")
