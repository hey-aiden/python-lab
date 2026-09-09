"""set_auth 端点 + get_cache_time TTL 逻辑的测试。

覆盖：
- get_cache_time：按缓存类型映射 TTL（user_name→20 / user_account→60 / 其他→180）
- set_auth 端点：调用 redis.setex 时传入映射后的 TTL
- set_auth 端点：领域异常 → HTTP 状态码（503 / 400，走全局异常处理器）
"""

import pytest

from app.deps import get_redis
from app.main import app
from app.services.errors import RedisResponseError, RedisUnavailableError
from app.services.redis_config import get_cache_time


class _FakeRedisService:
    """模拟 RedisService：记录 setex 调用参数，或按需抛领域异常。"""

    def __init__(self, exc: Exception | None = None):
        self.exc = exc
        self.setex_calls: list[tuple[str, int, str]] = []

    async def setex(self, key: str, ttl: int, value: str) -> bool:
        if self.exc:
            raise self.exc
        self.setex_calls.append((key, ttl, value))
        return True


@pytest.fixture(autouse=True)
def _clean_overrides():
    yield
    app.dependency_overrides.clear()


# ---- get_cache_time：TTL 映射 ----


@pytest.mark.parametrize(
    ("cache_type", "expected_ttl"),
    [
        ("user_name", 20),
        ("user_account", 60),
        ("unknown", 180),
    ],
)
def test_get_cache_time(cache_type: str, expected_ttl: int):
    assert get_cache_time(cache_type) == expected_ttl


# ---- set_auth 端点：TTL 透传 + 异常映射 ----


async def test_set_auth_stores_with_mapped_ttl(client):
    fake = _FakeRedisService()
    app.dependency_overrides[get_redis] = lambda: fake
    resp = await client.post(
        "/redis/set_auth/foo", json={"value": "123", "type": "user_name"}
    )
    assert resp.status_code == 200
    assert fake.setex_calls == [("foo", 20, "123")]


async def test_set_auth_falls_back_to_long_ttl(client):
    fake = _FakeRedisService()
    app.dependency_overrides[get_redis] = lambda: fake
    resp = await client.post(
        "/redis/set_auth/foo", json={"value": "123", "type": "whatever"}
    )
    assert resp.status_code == 200
    assert fake.setex_calls == [("foo", 180, "123")]


async def test_set_auth_maps_unavailable_to_503(client):
    fake = _FakeRedisService(exc=RedisUnavailableError("Redis 连接失败"))
    app.dependency_overrides[get_redis] = lambda: fake
    resp = await client.post(
        "/redis/set_auth/foo", json={"value": "123", "type": "user_name"}
    )
    assert resp.status_code == 503
    assert resp.json()["detail"] == "Redis 连接失败"


async def test_set_auth_maps_response_error_to_400(client):
    fake = _FakeRedisService(exc=RedisResponseError("WRONGTYPE"))
    app.dependency_overrides[get_redis] = lambda: fake
    resp = await client.post(
        "/redis/set_auth/foo", json={"value": "123", "type": "user_name"}
    )
    assert resp.status_code == 400
