"""应用配置：统一从环境变量 / .env 读取并做类型校验。"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """项目配置，字段与 .env 变量一一对应（大小写不敏感）。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- Redis ----
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    # ---- Kafka ----
    kafka_bootstrap_servers: str = "127.0.0.1:9092"
    kafka_topic: str = "learn-topic"
    kafka_order_topic: str = "order-events"
    kafka_group_id: str = "learn-group"
    kafka_client_id: str = "redis-mq-app"
    kafka_auto_offset_reset: str = "earliest"

    @property
    def redis_url(self) -> str:
        """拼接 redis:// URL，供 redis.asyncio 客户端直接使用。"""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
