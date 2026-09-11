"""日志埋点接口测试：验证上报序列化 + 分区 key + 消费拉取，不依赖真实 Kafka。

用内存 fake 模拟 producer / consumer，通过 dependency_overrides 注入，
验证端点编排逻辑（topic、key、序列化、响应结构）。
"""

import json

import pytest

from app.config import settings
from app.deps import get_kafka_consumer, get_kafka_producer
from app.main import app


class _FakeProducer:
    """记录 produce 调用（topic / value / key），不真正连接 Kafka。"""

    def __init__(self):
        self.calls: list[tuple[str, str, str | None]] = []

    def produce(self, topic: str, value: str, key: str | None = None) -> None:
        self.calls.append((topic, value, key))


class _FakeConsumer:
    """按队列返回预置消息，模拟 poll。"""

    def __init__(self, messages: list[dict]):
        self._messages = list(messages)
        self.subscribed: list[str] | None = None

    def subscribe(self, topics: list[str]) -> None:
        self.subscribed = topics

    def consume(self, timeout: float = 1.0) -> dict | None:
        return self._messages.pop(0) if self._messages else None


@pytest.fixture(autouse=True)
def _clean_overrides():
    yield
    app.dependency_overrides.clear()


async def test_track_produces_event_with_user_key(client):
    fake = _FakeProducer()
    app.dependency_overrides[get_kafka_producer] = lambda: fake

    resp = await client.post(
        "/log/track",
        json={"event": "page_view", "user_id": "u1", "payload": {"page": "/home"}},
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"

    # produce 被调用一次，且 topic / key / 序列化正确
    assert len(fake.calls) == 1
    topic, value, key = fake.calls[0]
    assert topic == settings.kafka_topic
    assert key == "u1"  # key=user_id，保证同用户事件分区内有序
    data = json.loads(value)
    assert data["event"] == "page_view"
    assert data["payload"] == {"page": "/home"}
    assert "timestamp" in data


async def test_track_fills_server_timestamp_when_missing(client):
    fake = _FakeProducer()
    app.dependency_overrides[get_kafka_producer] = lambda: fake

    await client.post("/log/track", json={"event": "click", "user_id": "u2"})

    _, value, _ = fake.calls[0]
    assert json.loads(value)["timestamp"] is not None


async def test_recent_consumes_up_to_n_messages(client):
    fake = _FakeConsumer(
        [
            {"topic": "t", "partition": 0, "offset": 0, "key": "u1", "value": "{}"},
            {"topic": "t", "partition": 0, "offset": 1, "key": "u2", "value": "{}"},
        ]
    )
    app.dependency_overrides[get_kafka_consumer] = lambda: fake

    resp = await client.get("/log/recent", params={"n": 5})
    body = resp.json()

    assert resp.status_code == 200
    assert body["count"] == 2  # 队列里只有 2 条，拉完即止
    assert fake.subscribed == [settings.kafka_topic]
    assert len(body["data"]) == 2
