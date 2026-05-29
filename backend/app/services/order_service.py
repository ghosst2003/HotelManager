from datetime import date, datetime, timezone
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Order, OrderItem, OperationLog, User, AdditionalExpense
from app.utils.permissions import can_modify_record, can_delete_record


def _json_safe(value):
    """Convert date/datetime/Decimal to JSON-safe types."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _json_safe_dict(d: dict) -> dict:
    return {k: _json_safe(v) for k, v in d.items()}


def _calc_item_fields(item_data: dict) -> dict:
    """Calculate gross_profit and profit_margin from cost/sale prices and additional expenses."""
    cost = Decimal(str(item_data.get("cost_price", 0)))
    sale = Decimal(str(item_data.get("sale_price", 0)))
    gross = sale - cost

    # Add additional expenses profit to gross profit
    additional = item_data.get("additional_expenses") or []
    exp_profit_sum = sum(
        Decimal(str(e.get("profit", (e.get("expense", 0) - e.get("cost", 0))))) for e in additional
    )
    gross += exp_profit_sum

    margin = (gross / sale * 100).quantize(Decimal("0.01")) if sale > 0 else Decimal("0")
    item_data["gross_profit"] = float(gross)
    item_data["profit_margin"] = float(margin)
    return item_data


def _create_expenses(db: Session, order_item_id: int, expenses: list) -> None:
    """Create AdditionalExpense records for an order item."""
    for e in expenses:
        cost = Decimal(str(e.get("cost", 0)))
        expense_val = Decimal(str(e.get("expense", 0)))
        profit = expense_val - cost
        db.add(AdditionalExpense(
            order_item_id=order_item_id,
            item=e.get("item", ""),
            cost=cost,
            expense=expense_val,
            profit=profit,
        ))


def _replace_expenses(db: Session, order_item_id: int, expenses: list) -> None:
    """Delete existing expenses and create new ones for an order item."""
    db.query(AdditionalExpense).filter(
        AdditionalExpense.order_item_id == order_item_id,
    ).delete()
    _create_expenses(db, order_item_id, expenses)


class OrderService:
    @staticmethod
    def create_order(db: Session, order_data: dict, created_by: int, salesperson_name: str) -> Order:
        items_data = order_data.pop("items", [])
        order = Order(**order_data, created_by=created_by, salesperson=salesperson_name)
        db.add(order)
        db.flush()

        for item_data in items_data:
            expenses = item_data.pop("additional_expenses", None) or []
            item_data = _calc_item_fields(item_data)
            item = OrderItem(order_id=order.id, **item_data)
            db.add(item)
            db.flush()  # Get item.id
            _create_expenses(db, item.id, expenses)

        db.add(OperationLog(
            user_id=created_by,
            action="create",
            entity_type="order",
            entity_id=order.id,
            details={"order_platform": order_data["order_platform"], "order_number": order_data["order_number"]},
        ))
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def update_order(db: Session, order_id: int, update_data: dict, user: User) -> Order:
        order = db.query(Order).filter(Order.id == order_id, Order.is_deleted == 0).first()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")

        is_owner = order.created_by == user.id
        if not can_modify_record(order.created_at, user.role, is_owner):
            raise HTTPException(status_code=403, detail="超过一个月的记录不能修改")

        # Update scalar fields
        for key, value in update_data.items():
            if key == "items" or value is None:
                continue
            setattr(order, key, value)

        # Replace items if provided
        if "items" in update_data and update_data["items"] is not None:
            db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
            for item_data in update_data["items"]:
                expenses = item_data.pop("additional_expenses", None) or []
                item_data = _calc_item_fields(item_data)
                item = OrderItem(order_id=order_id, **item_data)
                db.add(item)
                db.flush()
                _create_expenses(db, item.id, expenses)

        db.add(OperationLog(
            user_id=user.id,
            action="update",
            entity_type="order",
            entity_id=order_id,
            details={"changes": _json_safe_dict({k: v for k, v in update_data.items() if k != "items"})},
        ))
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def soft_delete_order(db: Session, order_id: int, user: User) -> Order:
        order = db.query(Order).filter(Order.id == order_id, Order.is_deleted == 0).first()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")

        is_owner = order.created_by == user.id
        if not can_delete_record(order.created_at, user.role, is_owner):
            raise HTTPException(status_code=403, detail="超过一个月的记录不能删除")

        order.is_deleted = 1
        order.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
        order.deleted_by = user.id

        db.add(OperationLog(
            user_id=user.id,
            action="delete",
            entity_type="order",
            entity_id=order_id,
            details={"order_number": order.order_number, "order_platform": order.order_platform},
        ))
        db.commit()
        return order

    @staticmethod
    def get_order(db: Session, order_id: int, user: User) -> Order:
        order = db.query(Order).filter(Order.id == order_id, Order.is_deleted == 0).first()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        if user.role == "employee" and order.created_by != user.id:
            raise HTTPException(status_code=403, detail="无权查看他人订单")
        return order
