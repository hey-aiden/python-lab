"""冒烟测试：确认应用可启动、配置加载、路由已注册。"""


async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["redis_host"] == "127.0.0.1"
    assert data["kafka_bootstrap_servers"] == "127.0.0.1:9092"
