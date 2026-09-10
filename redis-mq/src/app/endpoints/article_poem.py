"""诗词投票数据接口。

数据模型：
- `poem:{id}`：诗词 JSON（SET），值为 PoemUploadRequest 字段 + group 的序列化结果（id 用 uuid4 生成）
- `poem:group:{group}`：该分组下诗词 ID 的集合（SADD，作为「分组 → 诗词」索引）
"""

import json
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.constants.redis_key import poem_group_key, poem_key
from app.deps import get_redis
from app.schemas.poem import PoemUpdateRequest, PoemUploadRequest
from app.services.redis_service import RedisService

router = APIRouter(prefix="/poem", tags=["poem"])


@router.post("/upload_poem/{group}")
async def upload_poem(
    group: str,
    body: PoemUploadRequest,
    redis: Annotated[RedisService, Depends(get_redis)],
):
    """上传一首诗词到指定分组，返回分配到的诗词 ID。

    - 用 uuid4 生成全局唯一 ID，同一分组可存多首、互不覆盖
    - 诗词本体存 `poem:{id}`，ID 加入 `poem:group:{group}` 集合作为分组索引
    """
    poem_id = uuid.uuid4().hex
    # poem_id = await redis.incr("poem:next_id")
    # 把 group 一并存入 JSON，删除时才能从分组索引里定位并移除
    data = {**body.model_dump(), "group": group}
    # json.dumps(ensure_ascii=False)：dict → JSON 字符串，中文不转义成 \uXXXX
    await redis.set(poem_key(poem_id), json.dumps(data, ensure_ascii=False))
    await redis.sadd(poem_group_key(group), poem_id)
    return {"id": poem_id, "group": group}


@router.get("/get_poem")
async def get_poem(
    poem_id: str,
    redis: Annotated[RedisService, Depends(get_redis)],
):
    """按 poem_id 读取一首诗词。"""
    poem_info = await redis.get(poem_key(poem_id))
    if poem_info is None:
        raise HTTPException(status_code=404, detail="诗词不存在")
    return {"id": poem_id, "data": json.loads(poem_info)}


@router.patch("/update_poem")
async def update_poem(
    poem_id: str,
    body: PoemUpdateRequest,
    redis: Annotated[RedisService, Depends(get_redis)],
):
    """部分更新一首诗词：只覆盖请求体里传入的字段，其余保持不变。"""
    existing = await redis.get(poem_key(poem_id))
    if existing is None:
        raise HTTPException(status_code=404, detail="诗词不存在")

    data = json.loads(existing)  # json.loads：JSON 字符串 → dict，还原旧值
    # model_dump(exclude_unset=True)：模型 → dict，且只含客户端「真正传入」的字段
    data.update(body.model_dump(exclude_unset=True))
    # json.dumps(ensure_ascii=False)：dict → JSON 字符串，中文不转义成 \uXXXX
    await redis.set(poem_key(poem_id), json.dumps(data, ensure_ascii=False))
    return {"id": poem_id, "data": data}


@router.delete("/delete_poem")
async def delete_poem(
    poem_id: str,
    redis: Annotated[RedisService, Depends(get_redis)],
):
    """删除一首诗词：删本体 + 从分组索引移除，不存在则 404。"""
    existing = await redis.get(poem_key(poem_id))
    if existing is None:
        raise HTTPException(status_code=404, detail="诗词不存在")

    group = json.loads(existing).get("group")
    await redis.delete(poem_key(poem_id))
    if group is not None:
        await redis.srem(poem_group_key(group), poem_id)
    return {"id": poem_id, "deleted": True}
