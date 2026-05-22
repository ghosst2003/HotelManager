from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, OperationLog
from app.auth import get_password_hash
from app.dependencies import require_role
from app.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        username=body.username,
        password_hash=get_password_hash(body.password),
        display_name=body.display_name,
        role=body.role,
    )
    db.add(user)
    db.add(OperationLog(
        user_id=current_user.id,
        action="user_create",
        entity_type="user",
        details={"username": body.username, "role": body.role},
    ))
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/toggle", response_model=UserResponse)
def toggle_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能禁用自己")

    user.is_active = 0 if user.is_active else 1
    action = "user_disable" if not user.is_active else "user_enable"
    db.add(OperationLog(
        user_id=current_user.id,
        action=action,
        entity_type="user",
        entity_id=user_id,
        details={"username": user.username},
    ))
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    db.add(OperationLog(
        user_id=current_user.id,
        action="user_delete",
        entity_type="user",
        entity_id=user_id,
        details={"username": user.username},
    ))
    db.delete(user)
    db.commit()
    return {"message": "删除成功"}
