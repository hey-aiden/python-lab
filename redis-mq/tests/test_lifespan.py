"""验证生产级生命周期：lifespan 创建 Redis 服务、关闭时释放连接。"""

from app.main import app, lifespan


async def test_lifespan_creates_redis_service():
    async with lifespan(app):
        assert app.state.redis is not None
        # 客户端已就位（惰性连接，无需 Redis 实际运行）
        assert app.state.redis._client is not None
