"""Kafka 服务层：producer / consumer / admin 操作标记（尚未实现）。

统一约定：
- 使用 `confluent-kafka`（同步客户端）。
- 后续接入 FastAPI async 端点时，通过 `run_in_executor` / 线程池包装同步调用。
- 连接参数来自 `app.config.settings`（bootstrap_servers / topic / group_id / client_id）。
"""


class KafkaProducerService:
    """生产者：发送消息。

    TODO: 实现 — 创建 `confluent_kafka.Producer`（bootstrap.servers、client.id）。
    """

    def produce(self, topic: str, value: str, key: str | None = None) -> None:
        """PRODUCE：异步投递一条消息（可带投递回调确认）。TODO: 实现"""
        raise NotImplementedError

    def flush(self, timeout: float = 10.0) -> int:
        """FLUSH：阻塞等待未投递消息全部送达。TODO: 实现"""
        raise NotImplementedError


class KafkaConsumerService:
    """消费者：订阅并拉取消息。

    TODO: 实现 — 创建 `confluent_kafka.Consumer`（group.id、auto.offset.reset）。
    """

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
        """CLOSE：关闭消费者，释放连接。TODO: 实现"""
        raise NotImplementedError


class KafkaAdminService:
    """管理端：主题操作。

    TODO: 实现 — 创建 `confluent_kafka.admin.AdminClient`。
    """

    def create_topic(self, topic: str, partitions: int = 1, replication: int = 1) -> None:
        """CREATE TOPIC：创建主题。TODO: 实现"""
        raise NotImplementedError

    def list_topics(self) -> list[str]:
        """LIST TOPICS：列出已有主题。TODO: 实现"""
        raise NotImplementedError


# 模块级单例：连接复用，避免每次请求新建客户端
producer_service = KafkaProducerService()
consumer_service = KafkaConsumerService()
admin_service = KafkaAdminService()
