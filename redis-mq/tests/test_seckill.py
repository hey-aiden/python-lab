"""秒杀抢购测试：Lua 原子下单/退款、SETNX 幂等初始化、分布式锁封盘。

用内存 fake 模拟 Redis 的 set_nx / get / set / eval / zcard，验证 SeckillService
编排逻辑（脚本选择、key 顺序、返回码）与分布式锁互斥，不依赖真实 Redis。
"""

import pytest

from app.constants.redis_key import seckill_stock_key
from app.deps import get_seckill
from app.main import app
from app.services.lock_service import _RELEASE_LOCK_SCRIPT, LockService
from app.services.seckill_service import (
    _SECKILL_ORDER_SCRIPT,
    _SECKILL_REFUND_SCRIPT,
    SeckillService,
)


class _FakeRedisService:
    """用内存 dict 模拟 Redis，按脚本常量分发 eval 行为。"""

    def __init__(self):
        self._store: dict[str, str] = {}
        self._zset: dict[str, dict[str, float]] = {}

    async def set_nx(self, key: str, value: str, ttl: int | None = None) -> bool:
        if key in self._store:
            return False
        self._store[key] = value
        return True

    async def set(self, key: str, value: str) -> bool:
        self._store[key] = value
        return True

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def zcard(self, key: str) -> int:
        return len(self._zset.get(key, {}))

    async def eval(self, script: str, numkeys: int, *keys_and_args: str):
        if script == _SECKILL_ORDER_SCRIPT:
            stock_key, order_key, orders_key, closed_key = keys_and_args[:4]
            user_id, ts = keys_and_args[4], keys_and_args[5]
            if closed_key in self._store:
                return -3
            if order_key in self._store:
                return -2
            stock = int(self._store.get(stock_key, "0"))
            if stock < 1:
                return -1
            self._store[stock_key] = str(stock - 1)
            self._store[order_key] = "1"
            self._zset.setdefault(orders_key, {})[user_id] = float(ts)
            return stock - 1
        if script == _SECKILL_REFUND_SCRIPT:
            order_key, stock_key, orders_key = keys_and_args[:3]
            user_id = keys_and_args[3]
            if order_key not in self._store:
                return 0
            del self._store[order_key]
            self._store[stock_key] = str(int(self._store.get(stock_key, "0")) + 1)
            self._zset.get(orders_key, {}).pop(user_id, None)
            return 1
        if script == _RELEASE_LOCK_SCRIPT:
            key, token = keys_and_args[0], keys_and_args[1]
            if self._store.get(key) == token:
                del self._store[key]
                return 1
            return 0
        raise AssertionError(f"未识别的脚本: {script}")


@pytest.fixture(autouse=True)
def _clean_overrides():
    yield
    app.dependency_overrides.clear()


def _install(fake: _FakeRedisService) -> None:
    app.dependency_overrides[get_seckill] = lambda: SeckillService(fake, LockService(fake))


async def _init(client, activity_id="a1", stock=5):
    return await client.post("/seckill/init", json={"activity_id": activity_id, "stock": stock})


async def _order(client, activity_id="a1", user_id="u1"):
    return await client.post("/seckill/order", json={"activity_id": activity_id, "user_id": user_id})


# ---- 初始化（SETNX 幂等）----


async def test_init_then_duplicate_rejected(client):
    fake = _FakeRedisService()
    _install(fake)

    first = await _init(client, stock=10)
    second = await _init(client, stock=20)

    assert first.json()["initialized"] is True
    assert second.json()["initialized"] is False
    assert fake._store[seckill_stock_key("a1")] == "10"  # 重复初始化不覆盖库存


# ---- 下单（Lua 原子）----


async def test_order_success_remaining(client):
    fake = _FakeRedisService()
    _install(fake)

    await _init(client, stock=2)
    r1 = await _order(client, user_id="u1")
    r2 = await _order(client, user_id="u2")

    assert r1.json()["success"] is True and r1.json()["remaining"] == 1
    assert r2.json()["success"] is True and r2.json()["remaining"] == 0


async def test_order_sold_out(client):
    fake = _FakeRedisService()
    _install(fake)

    await _init(client, stock=1)
    await _order(client, user_id="u1")
    r2 = await _order(client, user_id="u2")

    assert r2.json()["success"] is False and r2.json()["message"] == "已抢光"


async def test_order_duplicate_not_deduct_twice(client):
    fake = _FakeRedisService()
    _install(fake)

    await _init(client, stock=5)
    await _order(client, user_id="u1")
    r = await _order(client, user_id="u1")

    assert r.json()["success"] is False and r.json()["message"] == "已抢过"
    assert fake._store[seckill_stock_key("a1")] == "4"  # 库存只扣一次


# ---- 退款（Lua 原子）----


async def test_refund_restores_stock(client):
    fake = _FakeRedisService()
    _install(fake)

    await _init(client, stock=3)
    await _order(client, user_id="u1")
    assert fake._store[seckill_stock_key("a1")] == "2"

    r = await client.post("/seckill/refund", json={"activity_id": "a1", "user_id": "u1"})
    assert r.json()["refunded"] is True
    assert fake._store[seckill_stock_key("a1")] == "3"


async def test_refund_non_ordered(client):
    fake = _FakeRedisService()
    _install(fake)

    await _init(client, stock=3)
    r = await client.post("/seckill/refund", json={"activity_id": "a1", "user_id": "nobody"})
    assert r.json()["refunded"] is False


# ---- 封盘（分布式锁）----


async def test_close_settles_once(client):
    fake = _FakeRedisService()
    _install(fake)

    await _init(client, stock=5)
    await _order(client, user_id="u1")
    await _order(client, user_id="u2")

    r = await client.post("/seckill/close", json={"activity_id": "a1"})
    body = r.json()
    assert body["settled"] is True
    assert body["order_count"] == 2
    assert body["remaining"] == 3


async def test_close_when_lock_held(client):
    fake = _FakeRedisService()
    _install(fake)

    await _init(client, stock=5)
    # 模拟另一个实例已持有结算锁
    await LockService(fake).acquire("seckill:close:a1", ttl=10)

    r = await client.post("/seckill/close", json={"activity_id": "a1"})
    body = r.json()
    assert body["settled"] is False
    assert body["reason"] == "另一个实例正在结算"


async def test_order_after_close_rejected(client):
    fake = _FakeRedisService()
    _install(fake)

    await _init(client, stock=5)
    await client.post("/seckill/close", json={"activity_id": "a1"})

    r = await _order(client, user_id="u1")
    assert r.json()["success"] is False
    assert r.json()["message"] == "活动已结束"
    # 封盘后库存不应被扣减
    assert fake._store[seckill_stock_key("a1")] == "5"


# ---- 查询 ----


async def test_stock_and_result(client):
    fake = _FakeRedisService()
    _install(fake)

    assert (await client.get("/seckill/stock", params={"activity_id": "a1"})).json()["remaining"] is None
    await _init(client, stock=7)
    assert (await client.get("/seckill/stock", params={"activity_id": "a1"})).json()["remaining"] == 7

    assert (await client.get("/seckill/result", params={"activity_id": "a1", "user_id": "u1"})).json()["grabbed"] is False
    await _order(client, user_id="u1")
    assert (await client.get("/seckill/result", params={"activity_id": "a1", "user_id": "u1"})).json()["grabbed"] is True
