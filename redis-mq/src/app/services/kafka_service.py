"""Kafka 服务层：producer / consumer / admin（操作已实现，连接生命周期就绪）。

统一约定：
- 使用 `confluent-kafka`（同步客户端）。
- 由 FastAPI lifespan 在启动时实例化、关闭时 flush / close。
- produce 是非阻塞异步投递，可直接在 async 端点调用；
  poll / commit / flush 等阻塞调用，接入 async 端点时用 anyio.to_thread 包装。
"""

import logging

from confluent_kafka import Consumer, KafkaError, KafkaException, Producer
from confluent_kafka.admin import AdminClient

from app.config import settings

logger = logging.getLogger(__name__)


def _delivery_report(err, msg) -> None:
    """投递回调：在 producer 后台线程触发，是拿「是否送达」结论的唯一入口。

    produce() 只把消息放入本地缓冲队列（非阻塞），真正的网络发送与确认由
    librdkafka 后台线程完成；回调参数 err / msg 即送达结果。
    """
    if err is not None:
        logger.error("Kafka 投递失败: %s", err)
    else:
        logger.info(
            "Kafka 投递成功: topic=%s partition=%d offset=%d",
            msg.topic(),
            msg.partition(),
            msg.offset(),
        )


class KafkaProducerService:
    """生产者：发送消息。"""

    def __init__(self) -> None:
        # broker.address.family=v4：macOS 上 localhost 会优先解析成 IPv6 ::1，而 broker
        # 通常只监听 IPv4，导致重连 advertised 地址时被拒；强制 v4 绕开（见 docs/kafka.md 3.9）。
        self._producer = Producer(
            {
                "bootstrap.servers": settings.kafka_bootstrap_servers,
                "broker.address.family": "v4",
                "client.id": settings.kafka_client_id,
            }
        )

    def produce(self, topic: str, value: str, key: str | None = None) -> None:
        """PRODUCE：异步投递一条消息。

        - value / key 为 str（或 bytes）；key 用于分区路由，相同 key 落到同一
          分区，从而保证同 key 消息在分区内有序（日志埋点按 user_id 分区即为此）。
        - 非阻塞：仅写入本地缓冲队列，由后台线程批量发送，故可在 async 端点
          直接调用，无需 anyio.to_thread。
        - 送达结果由 _delivery_report 回调异步确认；flush() 阻塞等待全部送达。
        """
        self._producer.produce(topic, value=value, key=key, callback=_delivery_report)

    def flush(self, timeout: float = 10.0) -> int:
        """FLUSH：阻塞等待未投递消息全部送达（lifespan 关闭阶段也会调用）。"""
        return self._producer.flush(timeout)


class KafkaConsumerService:
    """消费者：订阅并拉取消息。"""

    def __init__(self) -> None:
        # broker.address.family=v4：同 producer，强制 IPv4，绕开 localhost→::1 的连接被拒。
        self._consumer = Consumer(
            {
                "bootstrap.servers": settings.kafka_bootstrap_servers,
                "broker.address.family": "v4",
                "group.id": settings.kafka_group_id,
                "auto.offset.reset": settings.kafka_auto_offset_reset,
                "client.id": settings.kafka_client_id,
            }
        )

    def subscribe(self, topics: list[str]) -> None:
        """SUBSCRIBE：订阅主题列表（重复订阅同名主题以最后一次为准）。"""
        self._consumer.subscribe(topics)

    def consume(self, timeout: float = 1.0) -> dict | None:
        """CONSUME：拉取一条消息，阻塞至 timeout 秒，无消息返回 None。

        返回 dict（topic / partition / offset / key / value），便于 endpoint 直接序列化；
        消费到分区末尾（EOF）返回 None，真实错误抛 KafkaException。
        此方法阻塞当前线程，async 端点请用 anyio.to_thread 包装。
        """
        msg = self._consumer.poll(timeout)
        if msg is None:
            return None
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                return None  # 已消费到分区末尾，非错误
            raise KafkaException(msg.error())
        return {
            "topic": msg.topic(),
            "partition": msg.partition(),
            "offset": msg.offset(),
            "key": msg.key().decode("utf-8") if msg.key() else None,
            "value": msg.value().decode("utf-8") if msg.value() else None,
        }

    def commit(self) -> None:
        """COMMIT：手动提交 offset（配合 enable.auto.commit=false 时使用）。"""
        self._consumer.commit()

    def close(self) -> None:
        """CLOSE：关闭消费者，释放连接（lifespan 关闭阶段调用）。"""
        self._consumer.close()


class KafkaAdminService:
    """管理端：主题操作。"""

    def __init__(self) -> None:
        # broker.address.family=v4：同 producer，强制 IPv4。
        self._admin = AdminClient(
            {
                "bootstrap.servers": settings.kafka_bootstrap_servers,
                "broker.address.family": "v4",
            }
        )

    def create_topic(self, topic: str, partitions: int = 1, replication: int = 1) -> None:
        """CREATE TOPIC：创建主题。TODO: 实现"""
        raise NotImplementedError

    def list_topics(self) -> list[str]:
        """LIST TOPICS：列出已有主题。TODO: 实现"""
        raise NotImplementedError
