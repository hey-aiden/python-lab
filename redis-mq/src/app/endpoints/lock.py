"""锁 / 并发控制路由 — 只做参数解析与调用 LockService，业务逻辑在 services 层。

每个端点 docstring 标注该锁的适用场景；完整机制对比见
`app/services/lock_service.py` 模块说明。
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.deps import get_lock
from app.schemas.lock import (
    CasRequest,
    DeductStockRequest,
    LockAcquireRequest,
    LockReleaseRequest,
    LockRenewRequest,
)
from app.services.lock_service import LockService

router = APIRouter(prefix="/lock", tags=["lock"])


@router.post("/distributed/acquire")
async def acquire_lock(
    body: LockAcquireRequest, lock: Annotated[LockService, Depends(get_lock)]
):
    """加分布式锁。抢到返回 token，抢不到（他人持有）返回 None。

    场景：跨进程/服务互斥 —— 防重复下单、定时任务只跑一个实例、缓存击穿保护。
    返回的 token 必须保存，用于后续 release / renew。
    """
    token = await lock.acquire(body.lock_name, body.ttl)
    return {"code": 0, "acquired": token is not None, "token": token}


@router.post("/distributed/release")
async def release_lock(
    body: LockReleaseRequest, lock: Annotated[LockService, Depends(get_lock)]
):
    """释放分布式锁（Lua 比对 token 才 DEL，防误删他人锁）。"""
    released = await lock.release(body.lock_name, body.token)
    return {"code": 0, "released": released}


@router.post("/distributed/renew")
async def renew_lock(
    body: LockRenewRequest, lock: Annotated[LockService, Depends(get_lock)]
):
    """续期分布式锁：业务未跑完时延长过期时间，防锁提前过期被他人抢占。"""
    renewed = await lock.renew(body.lock_name, body.token, body.ttl)
    return {"code": 0, "renewed": renewed}


@router.post("/optimistic/watch")
async def optimistic_update(
    body: CasRequest, lock: Annotated[LockService, Depends(get_lock)]
):
    """乐观锁（WATCH/MULTI/EXEC 事务）：仅当 key 当前值 == expected 才写入 new_value。

    场景：低冲突的读-改-写（余额、库存、文档版本号）。冲突返回 updated=False，由调用方重试。
    """
    updated = await lock.optimistic_update(body.key, body.expected, body.new_value)
    return {"code": 0, "updated": updated}


@router.post("/optimistic/cas")
async def compare_and_set(
    body: CasRequest, lock: Annotated[LockService, Depends(get_lock)]
):
    """乐观锁（Lua CAS）：一段 Lua 原子完成「比对 + 写」，比 WATCH 事务更简洁。

    场景同 /optimistic/watch，推荐优先用本接口。
    """
    updated = await lock.compare_and_set(body.key, body.expected, body.new_value)
    return {"code": 0, "updated": updated}


@router.post("/atomic/deduct_stock")
async def deduct_stock(
    body: DeductStockRequest, lock: Annotated[LockService, Depends(get_lock)]
):
    """扣库存（Lua 原子操作）：判断余量足够才扣，返回剩余库存，-1 表示库存不足。

    场景：防超卖 —— 「读余量 → 判断 → 扣减」若分步执行会并发超卖，Lua 原子化杜绝。
    使用前可先 `POST /redis/set/stock:{product_id}` 写入初始库存（body {"value": "100"}）。
    """
    remaining = await lock.deduct_stock(body.product_id, body.amount)
    if remaining < 0:
        return {"code": 0, "success": False, "message": "库存不足"}
    return {"code": 0, "success": True, "remaining": remaining}
