from pydantic import BaseModel


class RequestContent(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    session_id: str | None = None  # 从 Cookie() 读取
    client_ip: str | None = None   # 从 request.client 读取
    method: str | None = None      # 从 request.method 读取
    path: str | None = None        # 从 request.url.path 读取
    user_agent: str | None = None  # 从 request.headers 读取


class HelloResponse(BaseModel):
    message: str


class SayHiResponse(BaseModel):
    msg: str


class FormResponse(BaseModel):
    user_name: str
