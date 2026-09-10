"""锁接口测试：分布式锁 / 乐观锁 / Lua 原子操作。

用内存 fake 模拟 Redis 的 set_nx / eval / pipeline 行为，验证 LockService 的
编排逻辑（脚本选择、参数顺序、冲突处理），不依赖真实 Redis。
"""

import pytest
from redis import asyncio as redis_asyncio

from app.constants.redis_key import stock_key
from app.deps import get_lock
from app.main import app
from app.services.lock_service import (
    _CAS_SCRIPT,
    _DEDUCT_STOCK_SCRIPT,
    _RELEASE_LOCK_SCRIPT,
    _RENEW_LOCK_SCRIPT,
    LockService,
)


class _FakePipeline:
    """模拟 redis.asyncio Pipeline：支持 watch/get/multi/set/execute/reset。"""

    def __init__(self, svc: "_FakeRedisService", conflict_on_execute: bool = False):
        self._svc = svc
        self._conflict_on_execute = conflict_on_execute
        self._multi = False
        self._pending: list[tuple[str, str, str]] = []

    async def watch(self, key: str) -> None:
        self._multi = False

    async def get(self, key: str) -> str | None:
        return self._svc._store.get(key)

    def multi(self) -> None:
        self._multi = True

    def set(self, key: str, value: str) -> None:
        if self._multi:
            self._pending.append(("set", key, value))

    async def execute(self) -> list:
        if self._conflict_on_execute:
            raise redis_asyncio.WatchError("key changed during watch")
        for op, key, value in self._pending:
            if op == "set":
                self._svc._store[key] = value
        self._pending = []
        return [True]

    async def reset(self) -> None:
        self._multi = False
        self._pending = []


class _FakeRedisService:
    """用内存 dict 模拟 Redis，按脚本常量分发 eval 行为。"""

    def __init__(self, conflict_on_execute: bool = False):
        self._store: dict[str, str] = {}
        self._conflict_on_execute = conflict_on_execute

    async def set_nx(self, key: str, value: str, ttl: int) -> bool:
        if key in self._store:
            return False
        self._store[key] = value
        return True

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def set(self, key: str, value: str) -> bool:
        self._store[key] = value
        return True

    async def eval(self, script: str, numkeys: int, *keys_and_args: str):
        key = keys_and_args[0]
        if script == _RELEASE_LOCK_SCRIPT:
            token = keys_and_args[1]
            if self._store.get(key) == token:
                del self._store[key]
                return 1
            return 0
        if script == _RENEW_LOCK_SCRIPT:
            token = keys_and_args[1]
            return 1 if self._store.get(key) == token else 0
        if script == _CAS_SCRIPT:
            expected, new_value = keys_and_args[1], keys_and_args[2]
            if self._store.get(key) == expected:
                self._store[key] = new_value
                return 1
            return 0
        if script == _DEDUCT_STOCK_SCRIPT:
            amount = int(keys_and_args[1])
            stock = int(self._store.get(key, "0"))
            if stock >= amount:
                self._store[key] = str(stock - amount)
                return stock - amount
            return -1
        raise AssertionError(f"未识别的脚本: {script}")

    def pipeline(self) -> _FakePipeline:
        return _FakePipeline(self, self._conflict_on_execute)


@pytest.fixture(autouse=True)
def _clean_overrides():
    yield
    app.dependency_overrides.clear()


def _install(fake: _FakeRedisService) -> None:
    app.dependency_overrides[get_lock] = lambda: LockService(fake)


# ---- 分布式锁 ----


async def test_acquire_then_conflict(client):
    fake = _FakeRedisService()
    _install(fake)

    first = (await client.post("/lock/distributed/acquire", json={"lock_name": "order", "ttl": 10})).json()
    second = (await client.post("/lock/distributed/acquire", json={"lock_name": "order", "ttl": 10})).json()

    assert first["acquired"] is True and first["token"]
    assert second["acquired"] is False and second["token"] is None


async def test_release_with_correct_token(client):
    fake = _FakeRedisService()
    _install(fake)

    token = (await client.post("/lock/distributed/acquire", json={"lock_name": "order", "ttl": 10})).json()["token"]
    resp = await client.post("/lock/distributed/release", json={"lock_name": "order", "token": token})
    assert resp.json()["released"] is True
    assert "lock:order" not in fake._store


async def test_release_with_wrong_token_does_not_delete(client):
    fake = _FakeRedisService()
    _install(fake)

    await client.post("/lock/distributed/acquire", json={"lock_name": "order", "ttl": 10})
    resp = await client.post("/lock/distributed/release", json={"lock_name": "order", "token": "other-token"})
    assert resp.json()["released"] is False
    assert "lock:order" in fake._store


async def test_renew_with_correct_token(client):
    fake = _FakeRedisService()
    _install(fake)

    token = (await client.post("/lock/distributed/acquire", json={"lock_name": "order", "ttl": 10})).json()["token"]
    resp = await client.post("/lock/distributed/renew", json={"lock_name": "order", "token": token, "ttl": 30})
    assert resp.json()["renewed"] is True


# ---- 乐观锁 ----


async def test_optimistic_cas_hit_and_miss(client):
    fake = _FakeRedisService()
    fake._store["doc"] = "v1"
    _install(fake)

    hit = await client.post("/lock/optimistic/cas", json={"key": "doc", "expected": "v1", "new_value": "v2"})
    miss = await client.post("/lock/optimistic/cas", json={"key": "doc", "expected": "v1", "new_value": "v3"})

    assert hit.json()["updated"] is True
    assert miss.json()["updated"] is False
    assert fake._store["doc"] == "v2"


async def test_optimistic_watch_hit(client):
    fake = _FakeRedisService()
    fake._store["doc"] = "v1"
    _install(fake)

    resp = await client.post("/lock/optimistic/watch", json={"key": "doc", "expected": "v1", "new_value": "v2"})
    assert resp.json()["updated"] is True
    assert fake._store["doc"] == "v2"


async def test_optimistic_watch_wrong_expected(client):
    fake = _FakeRedisService()
    fake._store["doc"] = "v9"
    _install(fake)

    resp = await client.post("/lock/optimistic/watch", json={"key": "doc", "expected": "v1", "new_value": "v2"})
    assert resp.json()["updated"] is False
    assert fake._store["doc"] == "v9"


async def test_optimistic_watch_conflict_raises_watch_error():
    # WATCH 提交瞬间被他人改动的冲突（EXEC 抛 WatchError）→ 返回 False
    fake = _FakeRedisService(conflict_on_execute=True)
    fake._store["doc"] = "v1"
    svc = LockService(fake)

    assert await svc.optimistic_update("doc", "v1", "v2") is False


# ---- Lua 原子操作 ----


async def test_deduct_stock_success(client):
    fake = _FakeRedisService()
    fake._store[stock_key(1)] = "10"
    _install(fake)

    resp = await client.post("/lock/atomic/deduct_stock", json={"product_id": 1, "amount": 3})
    body = resp.json()

    assert body["success"] is True and body["remaining"] == 7
    assert fake._store[stock_key(1)] == "7"


async def test_deduct_stock_insufficient(client):
    fake = _FakeRedisService()
    fake._store[stock_key(1)] = "2"
    _install(fake)

    resp = await client.post("/lock/atomic/deduct_stock", json={"product_id": 1, "amount": 5})
    body = resp.json()

    assert body["success"] is False and body["message"] == "库存不足"
    assert fake._store[stock_key(1)] == "2"
