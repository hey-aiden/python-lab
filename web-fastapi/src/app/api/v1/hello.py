import logging
from typing import Annotated

from fastapi import APIRouter, Body, Cookie, Form, HTTPException, Request, UploadFile

from app.schemas.hello import (
    FileResponse,
    FormResponse,
    HelloResponse,
    RequestContent,
    SayHiResponse,
)
from app.services.errors import ForbiddenError, NotFoundError
from app.services.hello import get_form, get_greeting, say_hi
from app.utils import safe_write

# Annotated[真实类型, 元数据] = 默认值 — 把类型、来源、默认值三者分离
#
# 什么时候需要 Annotated？
#   ✅ 简单类型 + 非默认来源 — 需要显式告诉 FastAPI 数据来自哪：
#     session: Annotated[str | None, Cookie()] = None   # 从 cookie 取
#     msg: Annotated[str, Body(embed=True)]              # 从 JSON body 取
#
#   ❌ 类型本身就能说明来源 — 不需要 Annotated：
#     body: RequestContent    # Pydantic 模型 → 自动从 JSON body 取
#     file: UploadFile        # FastAPI 内置类型 → 自动从 form-data 取
#     request: Request        # 特殊类型 → 自动注入整个 Request 对象
#     item_id: str            # 路径/查询参数 → 自动从路径或 ?key=value 取
#
# 对比不用 Annotated 的写法：
#   session: str = Cookie(default=None)        # Cookie() 占了 default 的位置，混淆
#   session: Annotated[str | None, Cookie()] = None  # 类型 + 来源 + 默认值 清晰分离


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/req_ctx", response_model=RequestContent)
def checkReq(
    request: Request,
    body: RequestContent,
    # Annotated[类型, 来源] = 默认值  — 三者清晰分离
    session: Annotated[str | None, Cookie()] = None,
):
    """接收 JSON body + 原始 Request，返回请求上下文（含客户端信息）."""
    body.session_id = session  # Cookie() 提取
    body.client_ip = request.client.host  # Request.client
    body.method = request.method  # Request.method
    body.path = request.url.path  # Request.url.path
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


# ─── 文件上传：三种写入方式 ───


# ─── 文件上传：三种写入方式，异常处理统一走 safe_write() ───


@router.post("/upload", response_model=FileResponse)
async def uploadFile(file: UploadFile):
    """方式 1：write_bytes — 最简洁，内部自动 with open("wb")."""
    content = await file.read()
    await file.close()
    safe_write("assets/upload", file.filename, content)
    return {"status": True}


@router.post("/upload/open", response_model=FileResponse)
async def upload_with_open(file: UploadFile):
    """方式 2：with open("wb") — 手动控制，可以分块写入，适合大文件.

    和 write_bytes 的区别：with open 可以指定 mode（"ab" 追加）、buffering 等。
    """
    from pathlib import Path

    content = await file.read()
    await file.close()

    target = Path("assets") / file.filename
    Path("assets").mkdir(exist_ok=True)
    with open(target, "wb") as f:  # "wb" 二进制写入，不能用文本 "w"
        f.write(content)

    return {"status": True}


@router.post("/upload/async", response_model=FileResponse)
async def upload_with_anyio(file: UploadFile):
    """方式 3：anyio.to_thread — 写入扔到线程池执行，不阻塞 asyncio 事件循环.

    生产环境推荐——大文件写入时其他请求不会被卡住。
    """
    import anyio

    content = await file.read()
    await file.close()

    await anyio.to_thread.run_sync(safe_write, "assets", file.filename, content)
    # safe_write 内部的异常（FileExistsError/PermissionError/OSError）
    # 会通过 anyio 自动传播回这里，触发 FastAPI 的异常处理

    return {"status": True}
