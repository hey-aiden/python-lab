# redis-mq

学习 **Redis** 与 **Kafka 消息队列** 的独立 FastAPI 应用。

当前状态：**脚手架 + 配置 + 分层结构**已就绪；Redis 的 `get`/`set`（含异常处理）已实现，其余操作仍为桩（`raise NotImplementedError`）。

## 目录结构

```
redis-mq/
├── pyproject.toml            # uv 管理依赖
├── Makefile                  # run / test 快捷命令
├── docker-compose.yml        # 只起 Redis
├── .env                      # 真实配置（gitignore）
├── env.example               # 配置模板（入库）
└── src/app/
    ├── config.py             # Settings：redis_* / kafka_* 字段
    ├── deps.py               # 依赖注入（从 app.state 取服务实例）
    ├── main.py               # FastAPI 入口 + lifespan + /health
    ├── endpoints/            # 路由层（标记桩）
    │   ├── redis_endpoints.py
    │   └── kafka_endpoints.py
    ├── services/             # 业务层（纯 Python，标记桩）
    │   ├── errors.py         # 领域异常（RedisUnavailableError 等）
    │   ├── redis_service.py  # 完整数据结构
    │   ├── kafka_service.py  # producer / consumer / admin
    │   └── redis-exceptions.md  # redis-py 异常类型说明
    └── schemas/              # 请求/响应模型
```

## 快速开始

```bash
# 1. 安装依赖
uv sync

# 2. 启动 Redis（本地 docker）
docker compose up -d

# 3. 启动服务（默认 8000 端口）
uv run dev

# 4. 健康检查
curl http://127.0.0.1:8000/health

# 5. 运行测试
uv run pytest
```

## 配置说明

配置统一从 `.env` 读取，由 `src/app/config.py` 的 `Settings` 做类型校验（pydantic-settings，大小写不敏感）。首次使用复制模板：

```bash
cp env.example .env
```

- **Redis**：`REDIS_HOST` / `REDIS_PORT` / `REDIS_DB` / `REDIS_PASSWORD`
- **Kafka**：`KAFKA_BOOTSTRAP_SERVERS` / `KAFKA_TOPIC` / `KAFKA_GROUP_ID` / `KAFKA_CLIENT_ID` / `KAFKA_AUTO_OFFSET_RESET`

## 技术选型

- **Redis 客户端**：`redis-py`（`redis.asyncio` 异步客户端，`redis_service.py` 方法为 `async`）
- **Kafka 客户端**：`confluent-kafka`（同步，接入 async 端点时通过线程池包装）
- **生命周期**：服务由 FastAPI `lifespan` 创建/释放，经 `deps.py` 的 `Depends` 注入端点（fork 安全、事件循环正确）

## 实现进度

| 模块 | 内容 | 状态 |
|------|------|------|
| `redis_service.py` | string / hash / list / set / zset / 过期 / 管道 / 发布订阅 | `get`/`set` 已实现（含异常处理），其余已标记 |
| `kafka_service.py` | producer / consumer / admin | 已标记 |
| `endpoints/*` | 代表性路由 | `get`/`set` 已实现，其余已标记 |

## 参考文档

- [redis-py 异常类型说明](src/app/services/redis-exceptions.md)
