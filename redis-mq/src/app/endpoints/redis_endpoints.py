"""Redis 相关路由 — 只负责路由分发与参数解析，业务逻辑下沉到 services 层。

分层约定（对齐 web-fastapi）：
- 本层：解析路径/查询/body 参数 → 调用 RedisService → 封装响应
- services 层：纯 Redis 操作逻辑，不依赖 FastAPI
- 异常映射：领域异常 → HTTP 状态码，统一由全局异常处理器完成
  （见 app/exception_handlers.py），endpoint 无需各自 try/except
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.deps import get_redis
from app.schemas.redis import SetexRequest, SetRequest
from app.services.redis_config import get_cache_time
from app.services.redis_service import RedisService

router = APIRouter(prefix="/redis", tags=["redis"])


@router.get("/get")
async def get_string(key: str, redis: Annotated[RedisService, Depends(get_redis)]):
    """读取 string：GET /redis/get?key=xxx。"""
    return await redis.get(key)


@router.post("/set/{key}")
async def set_string(
    key: str,
    body: SetRequest,
    redis: Annotated[RedisService, Depends(get_redis)],
):
    """写入 string：POST /redis/set/{key}，JSON body 为 {"value": "..."}。"""
    return await redis.set(key, body.value)


@router.post("/set_auth/{key}")
async def set_auth(
    key: str,
    body: SetexRequest,
    redis: Annotated[RedisService, Depends(get_redis)],
):
    """写入带 TTL 的 string：POST /redis/set_auth/{key}，JSON body 为 {"value": "...", "type": "..."}。"""
    ttl = get_cache_time(body.type)
    return await redis.setex(key, ttl, body.value)
