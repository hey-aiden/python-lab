"""全局中间件注册。

中间件执行流程（以 log_request_time 为例）：

  请求进入
    │
    ▼
  ┌─────────────────────────────────────────────┐
  │ start = time.perf_counter()    ← ① 进门：记录时间
  │ response = await call_next(req) ← ② 放行：交给路由 → endpoint → service
  │ elapsed = ...                  ← ③ 出门：拿到响应，计算耗时
  │ logger.info(...)               ← ④ 打印日志
  │ return response                ← ⑤ 返回给客户端
  └─────────────────────────────────────────────┘
    │
    ▼
  响应返回

  call_next 是分界线：
  - 之前 = 请求进来时做的事（记录、校验、注入等）
  - 之后 = 响应返回时做的事（日志、修改 header 等）"""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


def setup_middleware(app: FastAPI) -> None:
    """注册所有全局中间件。在 main.py 中调用一次即可。"""

    # CORS — 允许浏览器跨域访问（SSE EventSource 必需）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],       # 生产环境改为具体域名，如 ["http://localhost:3000"]
        allow_credentials=True,    # 允许携带 cookie
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_request_time(request: Request, call_next):
        """记录每个请求的耗时。"""
        start = time.perf_counter()  # ① 进门
        response = await call_next(request)  # ② 放行（分界线）
        elapsed = time.perf_counter() - start  # ③ 出门
        logger.info(  # ④ 日志
            "%s %s — %d (%.3fs)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
        )
        return response  # ⑤ 返回
