from pydantic import BaseModel


class PoemUploadRequest(BaseModel):
    title: str
    content: str
    author: str
    author_id: str


class PoemUpdateRequest(BaseModel):
    """诗词部分更新请求体：字段全部可选，只更新传入的字段。"""

    title: str | None = None
    content: str | None = None
    author: str | None = None
    author_id: str | None = None
    group: str | None = None
