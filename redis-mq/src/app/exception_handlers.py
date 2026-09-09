"""全局异常处理器 — 把领域异常统一映射为 HTTP 响应。

分层约定（对齐 web-fastapi）：
- service 层抛领域异常（RedisUnavailableError / RedisResponseError）
- 本层把领域异常翻译成 HTTP 状态码，endpoint 层无需各自 try/except
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.services.errors import RedisResponseError, RedisUnavailableError


def register_exception_handlers(app: FastAPI) -> None:
    """在 app 上注册领域异常 → HTTP 状态码的映射。"""

    @app.exception_handler(RedisUnavailableError)
    async def _redis_unavailable(request: Request, exc: RedisUnavailableError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @app.exception_handler(RedisResponseError)
    async def _redis_response_error(request: Request, exc: RedisResponseError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
