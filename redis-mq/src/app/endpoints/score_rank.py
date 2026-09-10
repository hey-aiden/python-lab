"""排行榜接口：写入分数 + 查询 top3。

数据模型：
- `rank:score`：zset，member=user_id、score=分数，用于排名
- `rank:player:{user_id}`：hash，存 name / class / age / gender 等详情
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.constants.redis_key import player_info_key, score_rank_key
from app.deps import get_redis
from app.schemas.score import ScoreRequest
from app.services.redis_service import RedisService

router = APIRouter(prefix="/rank", tags=["rank"])


@router.post("/add_score")
async def add_score(
    body: ScoreRequest, redis: Annotated[RedisService, Depends(get_redis)]
):
    """写入分数：zset 记排名（member=user_id），hash 记详情。"""
    user_id = uuid.uuid4().hex
    await redis.zadd(score_rank_key(), {user_id: body.score})
    await redis.hset(
        player_info_key(user_id),
        {
            "name": body.name,
            "class": body.class_name,
            "age": str(body.age),
            "gender": body.gender,
        },
    )
    return {"code": 0, "user_id": user_id, "name": body.name, "score": body.score}


@router.get("/top3")
async def top3(redis: Annotated[RedisService, Depends(get_redis)]):
    """获取分数排名 top3（降序）。"""
    top = await redis.zrevrange(score_rank_key(), 0, 2, withscores=True)
    result = []
    for user_id, score in top:
        info = await redis.hgetall(player_info_key(user_id))
        age = info.get("age")
        result.append(
            {
                "name": info.get("name"),
                "score": score,
                "class": info.get("class"),
                "age": int(age) if age is not None else None,
                "gender": info.get("gender"),
            }
        )
    return {"code": 0, "data": result}
