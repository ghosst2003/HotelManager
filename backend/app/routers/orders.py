from datetime import date, datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Order, OrderItem, OperationLog
from app.dependencies import get_current_user, require_role
from app.schemas import OrderCreate, OrderUpdate, OrderResponse, PageResponse, OrderItemResponse
from app.services.order_service import OrderService
from app.utils.export import export_orders_to_excel

router = APIRouter(prefix="/api/orders", tags=["orders"])


def _order_to_response(order: Order) -> dict:
    """Convert Order ORM to response dict."""
    items = []
    for item in order.items:
        items.append(OrderItemResponse(
            id=item.id,
            date=item.date,
            room_count=item.room_count,
            cost_price=Decimal(str(item.cost_price)),
            sale_price=Decimal(str(item.sale_price)),
            gross_profit=Decimal(str(item.gross_profit)),
            profit_margin=Decimal(str(item.profit_margin)),
            salesperson=item.salesperson,
            confirmation_number=item.confirmation_number,
            remarks=item.remarks,
            created_at=item.created_at,
            updated_at=item.updated_at,
        ))

    return OrderResponse(
        id=order.id,
        order_platform=order.order_platform,
        order_number=order.order_number,
        room_name=order.room_name,
        guest_name=order.guest_name,
        salesperson=order.salesperson,
        hotel_name=order.hotel_name,
        guest_count=order.guest_count,
        booking_date=order.booking_date,
        confirmation_number=order.confirmation_number,
        order_status=order.order_status,
        other_remarks=order.other_remarks,
        created_by=order.created_by,
        is_deleted=bool(order.is_deleted),
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=items,
    )


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(
    body: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("employee", "admin"):
        raise HTTPException(status_code=403, detail="无权创建订单")
    order = OrderService.create_order(db, body.model_dump(), current_user.id, current_user.display_name)
    return _order_to_response(order)


@router.get("/", response_model=PageResponse)
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_platform: str | None = None,
    booking_date_start: date | None = None,
    booking_date_end: date | None = None,
    salesperson: str | None = None,
    order_status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Order).filter(Order.is_deleted == 0)

    if current_user.role == "employee":
        query = query.filter(Order.created_by == current_user.id)

    if order_platform:
        query = query.filter(Order.order_platform == order_platform)
    if booking_date_start:
        query = query.filter(Order.booking_date >= booking_date_start)
    if booking_date_end:
        query = query.filter(Order.booking_date <= booking_date_end)
    if salesperson:
        query = query.filter(Order.salesperson.like(f"%{salesperson}%"))
    if order_status:
        query = query.filter(Order.order_status == order_status)

    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[_order_to_response(o) for o in orders],
    )


@router.get("/export")
def export_orders(
    order_platform: str | None = Query(None),
    booking_date_start: date | None = Query(None),
    booking_date_end: date | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("finance", "admin")),
):
    query = db.query(Order).filter(Order.is_deleted == 0)
    if order_platform:
        query = query.filter(Order.order_platform == order_platform)
    if booking_date_start:
        query = query.filter(Order.booking_date >= booking_date_start)
    if booking_date_end:
        query = query.filter(Order.booking_date <= booking_date_end)

    orders = query.order_by(Order.created_at.desc()).all()

    db.add(OperationLog(
        user_id=current_user.id,
        action="export",
        entity_type="order",
        details={"count": len(orders)},
    ))
    db.commit()

    buffer = export_orders_to_excel(orders)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=orders.xlsx"},
    )


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = OrderService.get_order(db, order_id, current_user)
    return _order_to_response(order)


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    body: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = OrderService.update_order(db, order_id, body.model_dump(exclude_unset=True), current_user)
    return _order_to_response(order)


@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    OrderService.soft_delete_order(db, order_id, current_user)
    return {"message": "删除成功"}
