# MySQL + SQLAlchemy 踩坑记录

> 记录从零搭建 FastAPI + SQLAlchemy + MySQL 过程中遇到的所有问题和解决方案。

---

## 问题 1：MySQL 8.0 认证失败 — `caching_sha2_password`

### 现象

```python
pymysql.err.OperationalError: (1045, "Access denied for user 'root'@'...' (using password: YES)")
```

### 原因

MySQL 8.0 默认认证插件从 `mysql_native_password` 改成了 `caching_sha2_password`。PyMySQL 需要主动从服务端获取 RSA 公钥才能完成认证。

### 解决

在 `create_engine` 时加 `connect_args`：

```python
engine = create_engine(
    settings.database_url,
    connect_args={
        # None = 自动从服务端获取 RSA 公钥
        "server_public_key": None,
    },
)
```

> 另一个方案是在 MySQL 里把用户改回 `mysql_native_password`：
> ```sql
> ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY '你的密码';
> ```
> 但 PyMySQL 方案更简单，一行配置解决。

---

## 问题 2：Docker 容器 IP 显示 `172.18.0.1` 而非 `localhost`

### 现象

明明配的是 `host=localhost`，错误日志里却是：

```
Access denied for user 'root'@'172.18.0.1'
```

### 原因

MySQL 运行在 Docker 容器里，宿主机通过端口映射（`0.0.0.0:3306->3306`）连接时，流量经过 Docker 网桥。MySQL 容器看到的客户端 IP 是 Docker 网关地址 `172.18.0.1`，不是 `localhost`。

```
宿主机 (macOS)  →  Docker 网桥 (172.18.0.1)  →  MySQL 容器
                       ↑ MySQL 看到的客户端 IP
```

### 解决

给 MySQL 用户授权时用 `%` 而非 `localhost`：

```sql
-- 查看当前有哪些 root 用户
SELECT user, host FROM mysql.user WHERE user='root';

-- 如果没有 root@'%'，创建一个
CREATE USER 'root'@'%' IDENTIFIED BY '你的密码';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

Docker 启动时设好 `MYSQL_ROOT_HOST=%` 也可以：

```bash
docker run -e MYSQL_ROOT_PASSWORD=root123 \
           -e MYSQL_ROOT_HOST=% \
           mysql:8.0
```

---

## 问题 3：VARCHAR 必须指定长度

### 现象

密码正确、连接成功，但 `create_all` 报错：

```
sqlalchemy.exc.CompileError: (in table 'users', column 'name'):
  VARCHAR requires a length on dialect mysql
```

### 原因

SQLAlchemy 的 `Mapped[str]` 类型推断在不同数据库上行为不同：

| 数据库 | `Mapped[str]` 生成的 DDL |
|--------|--------------------------|
| SQLite | `VARCHAR`（不报错，SQLite 不管长度）|
| MySQL | `VARCHAR` **→ 报错！** MySQL 强制要求长度 |
| PostgreSQL | `VARCHAR`（PostgreSQL 用 `text` 就行，但也接受裸 VARCHAR）|

只用 `Mapped[str]` 不加 `String(n)` 就是埋坑——SQLite 上跑得好好的，一切 MySQL 就炸。

### 解决

**永远显式指定 `String(长度)`**：

```python
from sqlalchemy import String

# ❌ 只靠类型推断，MySQL 上会炸
name: Mapped[str] = mapped_column()

# ✅ 显式指定长度，所有数据库都一样行为
name: Mapped[str] = mapped_column(String(100))
email: Mapped[str] = mapped_column(String(200))
avatar_url: Mapped[str | None] = mapped_column(String(500), default=None)
```

长度建议：

| 字段 | 推荐长度 | 理由 |
|------|---------|------|
| 用户名 | `String(100)` | 大多数系统的上限 |
| 邮箱 | `String(200)` | RFC 最大 254，200 实际够用 |
| URL | `String(500)` | URL 理论上可以很长，500 覆盖绝大多数 |
| 简短标识 | `String(50)` | 如 slug、标签 |
| 长文本 | `Text` 而不是 `String` | 没有长度限制 |

---

## 问题 4：`.env` 不创建，密码写在代码里

### 现象

`config.py` 里写了 `db_password: str = "devroot123"`，改了密码就要改代码+提交 Git → 密码泄露风险。

### 解决

**密码永远放 `.env`，不写默认值**：

```python
# config.py — 敏感信息不给默认值，强制从 .env 读取
class Settings(BaseSettings):
    db_password: str = ""   # 空字符串 = 必须配置

    model_config = {"env_file": ".env"}
```

```env
# .env（不提交 Git）
db_password=root123
db_name=local_data
```

```gitignore
# .gitignore
.env
```

原则：**`config.py` 可以写安全的默认值（如 `localhost`、`3306`），密码类敏感信息只从 `.env` 读取。**

---

## 问题 5：lifespan 建表失败静默吞掉

### 现象

数据库没启动或连不上时，服务器能起来，但表没建成功。日志里只有一行被忽略的 warning。

### 原因

开发阶段为了方便，在 `lifespan` 的 `create_all` 外包了 `try/except`，异常被吞掉了。生产环境这句话就不该存在——应该用 Alembic。

### 解决

**三个环境三种策略**：

| 环境 | 建表方式 | 为什么 |
|------|---------|--------|
| 本地 SQLite | `create_all` in lifespan | 零配置，改了模型重启就生效 |
| 本地 MySQL | `create_all` in lifespan | 同上，但要确保 MySQL 已启动 |
| 生产环境 | Alembic `upgrade head` | 有迁移记录，可回退，多人协作 |

开发时如果怀疑建表没成功，跑这个快速诊断：

```bash
uv run python -c "
from app.core.db import engine
from app.models import Base
from sqlalchemy import inspect

print('metadata 收录:', list(Base.metadata.tables.keys()))
try:
    Base.metadata.create_all(bind=engine)
    print('数据库中的表:', inspect(engine).get_table_names())
except Exception as e:
    print(f'失败: {e}')
"
```

---

## 问题速查表

| 错误信息 | 一句话原因 | 修复 |
|---------|-----------|------|
| `Access denied ... caching_sha2_password` | MySQL 8.0 新认证机制 | `connect_args={"server_public_key": None}` |
| `Access denied ... @172.18.0.1` | Docker 网桥 IP 不在用户白名单 | `CREATE USER ...@'%'` 或 `MYSQL_ROOT_HOST=%` |
| `VARCHAR requires a length on dialect mysql` | MySQL 强制 VARCHAR(n) | 加 `String(100)` |
| 启动成功但表不存在 | 密码错/库名错/MySQL 没启动，被 try 吞了 | 跑诊断脚本看具体错误 |
| IDE 能跑，Docker 里报错 | `.env` 没挂进容器 | 检查 `docker-compose.yml` 的 `env_file` |
