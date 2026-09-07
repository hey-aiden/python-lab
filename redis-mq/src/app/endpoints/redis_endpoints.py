"""Redis 相关路由 — 只负责路由分发与参数解析，业务逻辑下沉到 services 层。

分层约定（对齐 web-fastapi）：
- 本层：解析路径/查询参数 → 调用 RedisService → 封装响应
- services 层：纯 Redis 操作逻辑，不依赖 FastAPI
"""

from fastapi import APIRouter

from app.services.redis_service import redis_service

router = APIRouter(prefix="/redis", tags=["redis"])


@router.get("/get/{key}")
async def get_string(key: str):
    """读取 string：GET {key}。"""
    return await redis_service.get(key)


@router.post("/set/{key}")
async def set_string(key: str, value: str):
    """写入 string：SET {key} {value}。"""
    return await redis_service.set(key, value)
