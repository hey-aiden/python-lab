"""会话（session）接口：登录创建会话 → 设置会话信息 → 读取用户信息。

数据模型：`session:{user_id}` 是一个 hash，字段为 user_name / login_time，
统一带 TTL（SESSION_TTL），到期自动过期删除。
"""

import time
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.constants.redis_key import session_key
from app.deps import get_redis
from app.schemas.session import SessionRequest
from app.services.redis_service import RedisService

router = APIRouter(prefix="/session", tags=["session"])

# 会话有效期（秒）：30 分钟
SESSION_TTL = 30 * 60


@router.post("/login")
async def login(redis: Annotated[RedisService, Depends(get_redis)]):
    """登录：生成 user_id 并创建会话（带 TTL），返回 user_id。"""
    user_id = uuid.uuid4().hex
    await redis.hset(session_key(user_id), {"login_time": int(time.time())})
    await redis.expire(session_key(user_id), SESSION_TTL)
    return {"code": 0, "user_id": user_id}


@router.post("/set_session")
async def set_session(
    body: SessionRequest, redis: Annotated[RedisService, Depends(get_redis)]
):
    """设置/更新会话中的用户信息，并刷新 TTL。"""
    await redis.hset(
        session_key(body.user_id),
        {"user_name": body.user_name, "login_time": int(time.time())},
    )
    await redis.expire(session_key(body.user_id), SESSION_TTL)
    return {"code": 0, "user_id": body.user_id}


@router.get("/user_info")
async def get_user_info(
    user_id: str, redis: Annotated[RedisService, Depends(get_redis)]
):
    """按 user_id 读取会话中的用户信息，不存在则 404。"""
    user_info = await redis.hgetall(session_key(user_id))
    if not user_info:
        raise HTTPException(status_code=404, detail="用户信息不存在")
    return {"code": 0, "data": user_info}
