from datetime import datetime

from pydantic import BaseModel


class PoemCreate(BaseModel):
    title: str
    author: str


class PoemResponse(BaseModel):
    """诗词响应模型（兼容单条和列表查询）."""

    id: int
    title: str
    author: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}  # ORM 对象可直接转 Pydantic
