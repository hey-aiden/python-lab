"""Kafka 服务层：producer / consumer / admin（操作标记，连接生命周期已就绪）。

统一约定：
- 使用 `confluent-kafka`（同步客户端）。
- 由 FastAPI lifespan 在启动时实例化、关闭时 flush / close。
- 业务操作（produce / consume / subscribe / commit / topic）为桩，接入 async 端点时
  用 anyio.to_thread 包装同步调用，避免阻塞事件循环。
"""

from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient

from app.config import settings


class KafkaProducerService:
    """生产者：发送消息。"""

    def __init__(self) -> None:
        self._producer = Producer(
            {
                "bootstrap.servers": settings.kafka_bootstrap_servers,
                "client.id": settings.kafka_client_id,
            }
        )

    def produce(self, topic: str, value: str, key: str | None = None) -> None:
        """PRODUCE：异步投递一条消息（可带投递回调确认）。TODO: 实现"""
        raise NotImplementedError

    def flush(self, timeout: float = 10.0) -> int:
        """FLUSH：阻塞等待未投递消息全部送达（lifespan 关闭阶段也会调用）。"""
        return self._producer.flush(timeout)


class KafkaConsumerService:
    """消费者：订阅并拉取消息。"""

    def __init__(self) -> None:
        self._consumer = Consumer(
            {
                "bootstrap.servers": settings.kafka_bootstrap_servers,
                "group.id": settings.kafka_group_id,
                "auto.offset.reset": settings.kafka_auto_offset_reset,
                "client.id": settings.kafka_client_id,
            }
        )

    def subscribe(self, topics: list[str]) -> None:
        """SUBSCRIBE：订阅主题列表。TODO: 实现"""
        raise NotImplementedError

    def consume(self, timeout: float = 1.0):
        """CONSUME：拉取一条消息（阻塞至超时，返回 Message 或 None）。TODO: 实现"""
        raise NotImplementedError

    def commit(self) -> None:
        """COMMIT：手动提交 offset（配合手动管理时使用）。TODO: 实现"""
        raise NotImplementedError

    def close(self) -> None:
        """CLOSE：关闭消费者，释放连接（lifespan 关闭阶段调用）。"""
        self._consumer.close()


class KafkaAdminService:
    """管理端：主题操作。"""

    def __init__(self) -> None:
        self._admin = AdminClient(
            {"bootstrap.servers": settings.kafka_bootstrap_servers}
        )

    def create_topic(self, topic: str, partitions: int = 1, replication: int = 1) -> None:
        """CREATE TOPIC：创建主题。TODO: 实现"""
        raise NotImplementedError

    def list_topics(self) -> list[str]:
        """LIST TOPICS：列出已有主题。TODO: 实现"""
        raise NotImplementedError
