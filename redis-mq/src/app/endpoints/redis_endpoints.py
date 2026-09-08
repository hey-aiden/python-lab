"""Redis 相关路由 — 只负责路由分发与参数解析，业务逻辑下沉到 services 层。

分层约定（对齐 web-fastapi）：
- 本层：解析路径/查询/body 参数 → 调用 RedisService → 封装响应
- services 层：纯 Redis 操作逻辑，不依赖 FastAPI
- 异常映射：领域异常 → HTTP 状态码（503 连接不可用 / 400 命令出错）
"""

from fastapi import APIRouter, Depends, HTTPException

from app.deps import get_redis
from app.schemas.redis import SetRequest
from app.services.errors import RedisResponseError, RedisUnavailableError
from app.services.redis_service import RedisService

router = APIRouter(prefix="/redis", tags=["redis"])


@router.get("/get")
async def get_string(key: str, redis: RedisService = Depends(get_redis)):
    """读取 string：GET /redis/get?key=xxx。"""
    try:
        return await redis.get(key)
    except RedisUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except RedisResponseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/set/{key}")
async def set_string(
    key: str,
    body: SetRequest,
    redis: RedisService = Depends(get_redis),
):
    """写入 string：POST /redis/set/{key}，JSON body 为 {"value": "..."}。"""
    try:
        return await redis.set(key, body.value)
    except RedisUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except RedisResponseError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
