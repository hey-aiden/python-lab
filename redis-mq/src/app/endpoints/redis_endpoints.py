"""Redis 相关路由（标记桩）。

TODO: 后续把每个数据结构操作暴露成 HTTP 端点。
路由层只做参数解析与响应封装，实际逻辑在 services/redis_service.py。
以下为代表性示例。
"""

from fastapi import APIRouter

router = APIRouter(prefix="/redis", tags=["redis"])


@router.get("/get/{key}")
async def get_string(key: str):
    """读取 string。TODO: 实现 — 调用 RedisService.get"""
    raise NotImplementedError


@router.post("/set/{key}")
async def set_string(key: str, value: str):
    """写入 string。TODO: 实现 — 调用 RedisService.set"""
    raise NotImplementedError
