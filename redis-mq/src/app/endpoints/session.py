from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.deps import get_redis
from app.schemas.session import SessionRequest
from app.services.redis_service import RedisService

router = APIRouter(prefix="/session", tags=["session"])


@router.post("/get_info")
async def get_session(
    body: SessionRequest, redis: Annotated[RedisService, Depends(get_redis)]
):
    session_id = body.session_id
    if session_id is None:
        raise HTTPException(status_code=404, detail="session_id为空")
    return {"session_id": session_id}
