"""用户 Pydantic 模型 — 请求/响应数据校验."""

from datetime import datetime

from pydantic import BaseModel, EmailStr

# ── 请求模型 ──


class UserCreate(BaseModel):
    """创建用户时客户端需要传的字段."""

    name: str
    email: EmailStr  # 自动校验邮箱格式，非法则 422
    avatar_url: str | None = None


class UserUpdate(BaseModel):
    """更新用户时客户端传的字段（全部可选，只更新传了的字段）."""

    name: str | None = None
    email: EmailStr | None = None
    avatar_url: str | None = None
    is_active: bool | None = None


# ── 响应模型 ──


class UserResponse(BaseModel):
    """返回给客户端的用户信息（包含 id 和时间戳）."""

    id: int
    name: str
    email: str
    avatar_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Pydantic v2: ORM 对象可直接转成此模型
    model_config = {"from_attributes": True}
