"""用户 API — 增删改查接口."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.errors import NotFoundError
from app.services.user import (
    create_user,
    delete_user,
    get_user,
    list_users,
    update_user,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/users", response_model=list[UserResponse])
def list_users_api(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    size: int = Query(20, ge=1, le=100, description="每页条数，上限 100"),
    db: Session = Depends(get_db),
):
    """分页查询用户列表，按创建时间倒序."""
    return list_users(db, page=page, size=size)


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_api(user_id: int, db: Session = Depends(get_db)):
    """按 ID 查询单个用户."""
    try:
        return get_user(db, user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/register", response_model=UserResponse, status_code=201)
def create_user_api(body: UserCreate, db: Session = Depends(get_db)):
    """创建新用户。邮箱格式由 Pydantic 自动校验."""
    return create_user(db, name=body.name, email=body.email, avatar_url=body.avatar_url)


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user_api(user_id: int, body: UserUpdate, db: Session = Depends(get_db)):
    """按 ID 更新用户。只更新请求体中传了的字段（PATCH 语义）."""
    try:
        return update_user(db, user_id, **body.model_dump(exclude_none=True))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/users/{user_id}", status_code=204)
def delete_user_api(user_id: int, db: Session = Depends(get_db)):
    """按 ID 删除用户."""
    try:
        delete_user(db, user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
