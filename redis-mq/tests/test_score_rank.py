"""排行榜接口测试：写入分数 + top3 降序返回。

用内存 fake 模拟 Redis zset/hash 的行为，验证 endpoint 的组装逻辑。
"""

import pytest

from app.deps import get_redis
from app.main import app


class _FakeRedisService:
    """用内存 dict 模拟 Redis zset + hash。"""

    def __init__(self):
        self._zset: dict[str, dict[str, float]] = {}
        self._hash: dict[str, dict[str, str]] = {}

    async def zadd(self, key: str, mapping: dict[str, float]) -> int:
        self._zset.setdefault(key, {}).update(mapping)
        return len(mapping)

    async def hset(self, name: str, mapping: dict[str, str]) -> int:
        self._hash.setdefault(name, {}).update(mapping)
        return len(mapping)

    async def zrevrange(self, key: str, start: int, stop: int, withscores: bool = False):
        items = sorted(self._zset.get(key, {}).items(), key=lambda kv: kv[1], reverse=True)
        items = items[start : stop + 1]
        return list(items) if withscores else [m for m, _ in items]

    async def hgetall(self, name: str) -> dict[str, str]:
        return self._hash.get(name, {})


@pytest.fixture(autouse=True)
def _clean_overrides():
    yield
    app.dependency_overrides.clear()


async def _add(client, name, score, class_name="一班", age=18, gender="m"):
    return await client.post(
        "/rank/add_score",
        json={"name": name, "score": score, "class": class_name, "age": age, "gender": gender},
    )


async def test_top3_returns_descending(client):
    fake = _FakeRedisService()
    app.dependency_overrides[get_redis] = lambda: fake

    for name, score in [("张三", 60), ("李四", 90), ("王五", 80), ("赵六", 95)]:
        resp = await _add(client, name, score)
        assert resp.status_code == 200

    data = (await client.get("/rank/top3")).json()["data"]
    assert [d["name"] for d in data] == ["赵六", "李四", "王五"]
    assert [d["score"] for d in data] == [95.0, 90.0, 80.0]


async def test_top3_merges_details(client):
    fake = _FakeRedisService()
    app.dependency_overrides[get_redis] = lambda: fake

    await _add(client, "张三", 100, class_name="二班", age=20, gender="f")

    data = (await client.get("/rank/top3")).json()["data"]
    assert data == [
        {"name": "张三", "score": 100.0, "class": "二班", "age": 20, "gender": "f"}
    ]


async def test_top3_empty(client):
    fake = _FakeRedisService()
    app.dependency_overrides[get_redis] = lambda: fake

    data = (await client.get("/rank/top3")).json()["data"]
    assert data == []
