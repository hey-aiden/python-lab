"""Redis 相关请求/响应模型。"""

from pydantic import BaseModel


class SetRequest(BaseModel):
    """SET 请求体：{"value": "..."}。"""

    value: str
