from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, OperationLog
from app.dependencies import require_role
from app.schemas import LogResponse, PageResponse

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("/", response_model=PageResponse)
def list_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    date_start: datetime | None = None,
    date_end: datetime | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    query = db.query(OperationLog)

    if user_id:
        query = query.filter(OperationLog.user_id == user_id)
    if action:
        query = query.filter(OperationLog.action == action)
    if entity_type:
        query = query.filter(OperationLog.entity_type == entity_type)
    if date_start:
        query = query.filter(OperationLog.created_at >= date_start)
    if date_end:
        query = query.filter(OperationLog.created_at <= date_end)

    total = query.count()
    logs = query.order_by(OperationLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[LogResponse(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            details=log.details,
            ip_address=log.ip_address,
            created_at=log.created_at,
        ) for log in logs],
    )
