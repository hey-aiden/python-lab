"""演示异常处理链路（无需 docker Redis）。

- service 层：捕获 redis-py 异常 → 抛领域异常
- endpoint 层：捕获领域异常 → HTTP 状态码
"""

import pytest
from redis import asyncio as redis_asyncio

from app.deps import get_redis
from app.main import app
from app.errors import RedisResponseError, RedisUnavailableError
from app.services.redis_service import RedisService


class _FakeClient:
    """模拟 redis.asyncio 客户端：按需抛 redis-py 异常。"""

    def __init__(self, exc: Exception | None = None):
        self.exc = exc

    async def get(self, key: str):
        if self.exc:
            raise self.exc
        return f"value:{key}"

    async def set(self, key: str, value: str):
        if self.exc:
            raise self.exc
        return True


class _FakeRedisService:
    """模拟 RedisService：按需抛领域异常（用于测试 endpoint 映射）。"""

    def __init__(self, exc: Exception | None = None):
        self.exc = exc

    async def get(self, key: str):
        if self.exc:
            raise self.exc
        return f"value:{key}"

    async def set(self, key: str, value: str):
        if self.exc:
            raise self.exc
        return True


@pytest.fixture(autouse=True)
def _clean_overrides():
    yield
    app.dependency_overrides.clear()


# ---- service 层：redis-py 异常 → 领域异常 ----


async def test_service_connection_error_raises_domain_error():
    svc = RedisService()
    svc._client = _FakeClient(exc=redis_asyncio.ConnectionError("down"))
    with pytest.raises(RedisUnavailableError):
        await svc.get("k")


async def test_service_response_error_raises_domain_error():
    svc = RedisService()
    svc._client = _FakeClient(exc=redis_asyncio.ResponseError("WRONGTYPE"))
    with pytest.raises(RedisResponseError):
        await svc.get("k")


# ---- endpoint 层：领域异常 → HTTP 状态码 ----


async def test_endpoint_maps_unavailable_to_503(client):
    app.dependency_overrides[get_redis] = lambda: _FakeRedisService(
        RedisUnavailableError("Redis 连接失败")
    )
    resp = await client.get("/redis/get", params={"key": "foo"})
    assert resp.status_code == 503
    assert resp.json()["detail"] == "Redis 连接失败"


async def test_endpoint_maps_wrongtype_to_400(client):
    app.dependency_overrides[get_redis] = lambda: _FakeRedisService(
        RedisResponseError("WRONGTYPE")
    )
    resp = await client.get("/redis/get", params={"key": "foo"})
    assert resp.status_code == 400


async def test_set_with_body_ok(client):
    app.dependency_overrides[get_redis] = lambda: _FakeRedisService()
    resp = await client.post("/redis/set/foo", json={"value": "123"})
    assert resp.status_code == 200
