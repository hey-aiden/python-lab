"""排行榜相关请求模型。"""

from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    """写入分数的请求体。class 是 Python 关键字，用 alias 映射到 class_name。"""

    name: str
    score: float
    class_name: str = Field(alias="class")
    age: int
    gender: str
