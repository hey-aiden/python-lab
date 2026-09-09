# Redis-MQ 实用笔记

> 本仓库（`redis-mq`）开发中沉淀的实用模式与约定，配合 `src/app` 源码阅读。
> 项目背景、命令见根目录 `CLAUDE.md` 与本项目 `README.md`。

## 目录

1. [分层架构与异常处理](#1-分层架构与异常处理)
2. [依赖注入：为什么用 Annotated](#2-依赖注入为什么用-annotated)
3. [Redis 常见数据模式](#3-redis-常见数据模式)
4. [redis-py 方法签名约定](#4-redis-py-方法签名约定)
5. [Key 命名约定](#5-key-命名约定)

---

## 1. 分层架构与异常处理

```
endpoint 层    →  解析参数、调 service、封装响应
service 层     →  纯 Redis 操作，不依赖 FastAPI
领域异常       →  RedisUnavailableError / RedisResponseError
全局 handler   →  领域异常 → HTTP 状态码
```

**异常三级流转：**

```
redis-py 异常 ──service 装饰器──▶ 领域异常 ──全局 handler──▶ HTTP
ConnectionError                    RedisUnavailableError         503
ResponseError                      RedisResponseError            400
```

**service 层用装饰器统一翻译**（`redis_service.py` 的 `_translate_errors`）：

```python
def _translate_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except redis_asyncio.ConnectionError as exc:
            raise RedisUnavailableError(f"Redis 连接失败: {exc}") from exc
        except redis_asyncio.ResponseError as exc:
            raise RedisResponseError(f"{func.__name__} 执行出错: {exc}") from exc
    return wrapper

@_translate_errors
async def incr(self, key: str) -> int:
    return await self._client.incr(key)
```

**要点：**

- service 层只做「翻译」，不吞异常、不碰 HTTP；`from exc` 保留原始堆栈。
- endpoint / 全局 handler（`exception_handlers.py`）把领域异常映射成 503/400。
- 个别方法需定制处理 → 不加装饰器、单独 `try/except`，但保持抛出的领域异常类型一致。

---

## 2. 依赖注入：为什么用 Annotated

```python
# ✅ Annotated（FastAPI 当前推荐）
async def upload_poem(redis: Annotated[RedisService, Depends(get_redis)]): ...

# ❌ = Depends(...) 会触发 Ruff B008
async def upload_poem(redis: RedisService = Depends(get_redis)): ...
```

- Ruff 的 **B008** 把「默认值里的函数调用」当潜在坑；对 FastAPI 的 `Depends` 是误报。
- `Annotated` 把 `Depends` 放进**类型注解**而非默认值，从根上消除 B008，无需 linter 白名单。
- 同时统一解决 `Query / Path / Body / Header / Form / File` 等同类 B008。
- 兼容性：`app.dependency_overrides[get_redis] = ...` 依旧生效（依赖还是同一个函数）。

---

## 3. Redis 常见数据模式

### 3.1 自增 ID（INCR）

```python
poem_id = await redis.incr("poem:next_id")   # → 1, 2, 3, ...
```

- `INCR` 原子「读 → +1 → 写」，并发下不重号；手动 `GET`+`SET` 有竞态。
- 键不存在时从 0 开始，第一次返回 1，无需先初始化。
- 值必须是整数，否则 `ERR value is not an integer or out of range`（→ `RedisResponseError` → 400）。

### 3.2 存对象：SET JSON 字符串 vs HSET

```python
# SET 整对象（简单，整存整取）
await redis.set(f"poem:{poem_id}", body.model_dump_json())

# HSET 按字段（可单独读写某字段）
await redis.hset(f"poem:{poem_id}", mapping=body.model_dump())
```

- Redis 值都是字符串；存对象要么序列化成 JSON 字符串，要么用 hash 按字段存。
- `model_dump_json()` 返回**字符串**（给 `SET` 用），`model_dump()` 返回 **dict**（给 `HSET` 用）。

### 3.3 分组索引（SADD）

```python
await redis.sadd(f"poem:group:{group}", str(poem_id))   # 集合：分组 → ID 列表
```

- 用集合记录「某分组下有哪些 ID」；配合 `SMEMBERS` 列出、`SISMEMBER` 判断，集合自动去重。
- 避免用 `KEYS poem:*` 扫 key（O(N)、阻塞），用集合做索引是正解。

### 3.4 计数器（INCR/DECR 的原子性）

```python
await redis.incr("page:home:views")   # 访问量 / 限流
await redis.decr("stock:item:100")    # 库存扣减
```

- 原子性让计数、限流、库存这类「读改写」场景无需加锁。

---

## 4. redis-py 方法签名约定

可变数量参数用 `*args`（定义时收集、调用时解包），对齐 Redis 命令本身：

```python
async def sadd(self, key: str, *members: str) -> int:
    return await self._client.sadd(key, *members)
# SADD key member [member ...] → 一次可加多个

async def hdel(self, name: str, *fields: str)      # HDEL key field [field ...]
async def srem(self, key: str, *members: str)      # SREM key member [member ...]
async def delete(self, *keys: str)                 # DEL key [key ...]
```

- 定义处 `*members`：收集任意多个位置参数成一个元组。
- 调用处 `*members`：把元组解包回独立参数传下去。

---

## 5. Key 命名约定

集中维护在 `app/constants/redis_key.py`：前缀是常量、拼 key 是函数，业务代码只调函数、不拼字符串。

```python
POEM_NS = "poem"

def poem_key(poem_id: int | str) -> str:   # poem:{id}
    return f"{POEM_NS}:{poem_id}"

def poem_group_key(group: str) -> str:     # poem:group:{group}
    return f"{POEM_NS}:group:{group}"
```

- 用 `:` 分层命名空间：`poem:{id}`、`poem:group:唐诗`。
- 诗词 ID 用 `uuid4` 生成（全局唯一、无需计数器）；若要改用 INCR 自增，再加一个 `poem_next_id_key()` 即可。
- 避免裸 key（如直接拿 `group` 当 key）——不同业务会撞车，且 `SET` 会互相覆盖。
