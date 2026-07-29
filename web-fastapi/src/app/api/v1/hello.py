import logging
from typing import Annotated

from fastapi import APIRouter, Body, Cookie, Form, HTTPException, Request

from app.schemas.hello import FormResponse, HelloResponse, RequestContent, SayHiResponse
from app.services.errors import ForbiddenError, NotFoundError
from app.services.hello import get_form, get_greeting, say_hi

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/req_ctx", response_model=RequestContent)
def checkReq(
    request: Request,
    body: RequestContent,
    session: Annotated[str | None, Cookie()] = None,
):
    """接收 JSON body + 原始 Request，返回请求上下文（含客户端信息）."""
    body.session_id = session         # Cookie() 提取
    body.client_ip = request.client.host       # Request.client
    body.method = request.method               # Request.method
    body.path = request.url.path               # Request.url.path
    body.user_agent = request.headers.get("user-agent")  # Request.headers
    return body


@router.get("/hello/{item_id}", response_model=HelloResponse)
def hello(item_id: str):
    """业务异常 → HTTP 状态码映射."""
    try:
        return get_greeting(item_id)
    except NotFoundError as e:
        logger.warning("资源不存在 item_id=%s: %s", item_id, e)
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/say_hi", response_model=SayHiResponse)
def sayHi(msg: str = Body(embed=True)):
    return say_hi(msg)


@router.post("/get_form", response_model=FormResponse)
def getForm(user_name: str = Form()):
    """接收 form-data，经过 service 处理后返回.

    Form() 匹配规则：
    - 参数名 user_name 自动匹配 form-data 中的 user_name 字段
    - 参数名和 form 字段不同时用 Form(alias="xxx")
    - 可选字段给默认值 Form(default="")
    """
    return get_form({"user_name": user_name})
