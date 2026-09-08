# redis-py（redis.asyncio）异常类型说明

`redis.asyncio` 会把 `redis.exceptions` 里的异常**全部 re-export**，所以
`redis_asyncio.ConnectionError` 和 `redis.exceptions.ConnectionError` 是同一个类，二者可互换。

所有异常统一继承自基类 `RedisError`。

## 异常层级

```
RedisError
├── ClusterError                     # 集群相关（本项目单机 Redis 用不到）
│   └── ClusterDownError
│       └── MasterDownError
├── ConnectionError                  # 连接层错误
│   ├── AuthenticationError          #   密码错误 / 认证失败
│   ├── AuthorizationError           #   无权限执行该命令
│   ├── BusyLoadingError             #   Redis 仍在从磁盘加载数据
│   ├── ExternalAuthProviderError    #   外部认证提供方错误
│   └── MaxConnectionsError          #   连接数耗尽（超过 maxclients）
├── DataError                        # 客户端传入的参数非法（在本地就抛出）
├── InvalidResponse                  # 服务端响应无法解析（协议异常，罕见）
├── LockError                        # 分布式锁相关
│   └── LockNotOwnedError            #   释放一个不属于自己的锁
├── PubSubError                      # 发布订阅相关
├── ResponseError                    # 服务端返回错误（命令执行失败）
│   ├── AskError                     #   集群 ask 重定向
│   │   └── MovedError               #   集群 moved 重定向
│   ├── AuthenticationWrongNumberOfArgsError
│   ├── ClusterCrossSlotError
│   ├── ExecAbortError               #   MULTI/EXEC 事务被中止
│   ├── ModuleError                  #   Redis 模块执行出错
│   ├── NoPermissionError            #   ACL 无权限
│   ├── NoScriptError                #   Lua 脚本未加载
│   ├── NoSuchFieldsetError
│   ├── OutOfMemoryError             #   Redis 内存不足
│   ├── ReadOnlyError                #   对只读副本执行了写命令
│   └── TryAgainError
├── TimeoutError                     # 命令超时（socket 超时）
└── WatchError                       # WATCH 乐观锁被破坏（事务）
```

> 完整清单可在运行环境里用以下命令查看：
> `python -c "from redis import exceptions; print([n for n in dir(exceptions) if n.endswith('Error')])"`

## 本项目会实际遇到的几类

| 异常 | 触发场景 | 本项目映射 |
|------|----------|-----------|
| `ConnectionError` | 网络断开、Redis 没启动、host/port 写错 | `RedisUnavailableError` → **503** |
| `AuthenticationError` | 密码错误（是 `ConnectionError` 子类） | 同上 → **503** |
| `TimeoutError` | 命令超时 | 建议 `RedisUnavailableError` → **503/504** |
| `ResponseError` | 服务端返回错误：WRONGTYPE、语法错误、ACL 无权限等 | `RedisResponseError` → **400** |
| `DataError` | 客户端参数非法（如 key 类型不对，**本地**抛出、不发请求） | 建议 **400** |
| `InvalidResponse` | 解析响应失败（协议异常，罕见） | 不捕获，交框架 **500** |

## 各异常详解

### ConnectionError 族 —— 「连不上」

- **`ConnectionError`**：最常遇到。Redis 进程没起、防火墙拦截、地址写错都会抛它。
- **`AuthenticationError`**：`.env` 里 `REDIS_PASSWORD` 与 Redis 实际 `--requirepass` 不一致。
- **`BusyLoadingError`**：Redis 重启后从 RDB/AOF 恢复数据期间，会拒绝部分命令。
- **`MaxConnectionsError`**：连接池被占满（`max_connections` 太小或代码泄漏连接）。

> 本项目用 `health_check_interval=30` + `retry_on_timeout=True` 缓解「重启后旧连接失效」的误报。

### ResponseError 族 —— 「连上了，但命令执行失败」

- 最常见是 **WRONGTYPE**：对已有 key 执行了类型不匹配的命令（如对 string 用 `HGET`），
  这是「客户端逻辑错误」，所以映射 400 而不是 500。
- **`ReadOnlyError`**：对只读副本执行写命令。
- **`NoScriptError`**：执行了未加载的 Lua 脚本。
- **`OutOfMemoryError`**：Redis 达到 `maxmemory` 上限。

### 其余（本项目暂不涉及）

`ClusterError` 族（集群）、`LockError`（分布式锁）、`WatchError`（事务乐观锁）、
`PubSubError`（发布订阅）——等用到对应特性时再按需捕获。

## 使用建议

1. **捕获顺序**：先具体后宽泛。`ConnectionError` 和 `ResponseError` 是兄弟关系，顺序无影响，
   但 `AuthenticationError` 是 `ConnectionError` 的子类，若要单独处理密码错误，必须写在 `ConnectionError` **之前**。
2. **保留异常链**：`raise RedisUnavailableError(...) from exc`，排查时能看到原始 redis-py 错误。
3. **兜底策略**：只捕获你**知道怎么处理**的异常；其余让它冒泡到框架返回 500，别吞掉。
4. **`DataError` 在本地抛**：它不产生网络往返，属于调用方传参错误，通常应在进入 service 前用 Pydantic 校验拦掉。
