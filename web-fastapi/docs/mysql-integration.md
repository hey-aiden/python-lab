# MySQL + SQLAlchemy 接入全流程

> 从零开始，把 FastAPI 项目接上 MySQL 数据库，按分层架构组织代码。每个文件和每行代码的逻辑都有解释。

---

## 目录

1. [依赖安装](#1-依赖安装)
2. [整体架构](#2-整体架构)
3. [文件清单与职责](#3-文件清单与职责)
4. [逐层解析](#4-逐层解析)
   - [4.1 配置层：`config.py`](#41-配置层configpy)
   - [4.2 数据库层：`core/db.py`](#42-数据库层coredbpy)
   - [4.3 模型层：`models/`](#43-模型层models)
   - [4.4 数据校验层：`schemas/`](#44-数据校验层schemas)
   - [4.5 业务逻辑层：`services/`](#45-业务逻辑层services)
   - [4.6 接口层：`api/v1/`](#46-接口层apiv1)
   - [4.7 启动入口：`main.py`](#47-启动入口mainpy)
5. [建表逻辑详解](#5-建表逻辑详解)
6. [完整请求追踪](#6-完整请求追踪)
7. [添加新表的步骤](#7-添加新表的步骤)

---

## 1. 依赖安装

```bash
uv add sqlalchemy pymysql email-validator
```

| 包 | 版本 | 角色 |
|---|------|------|
| `sqlalchemy` | ≥ 2.0 | ORM 框架 — 用 Python 对象操作数据库 |
| `pymysql` | ≥ 1.2 | MySQL 驱动 — 负责和 MySQL 服务器的底层通信 |
| `email-validator` | ≥ 2.3 | Pydantic `EmailStr` 的校验后端 |

> **`sqlalchemy` 和 `pymysql` 的关系**：SQLAlchemy 是"翻译官"，把 Python 代码翻译成 SQL；PyMySQL 是"邮递员"，把 SQL 送到 MySQL 服务器并带回结果。SQLAlchemy 不直接和 MySQL 通信，而是通过 PyMySQL。

`pyproject.toml` 中的最终依赖：

```toml
dependencies = [
    "email-validator>=2.3.0",
    "fastapi>=0.140.13",
    "pydantic-settings>=2.0.0",
    "pymysql>=1.2.0",
    "python-multipart>=0.0.32",
    "sqlalchemy>=2.0.51",
    "uvicorn>=0.51.0",
]
```

---

## 2. 整体架构

```
请求进入                     FastAPI 分层                         数据库
─────────────────────────────────────────────────────────────────────

GET /api/v1/users/1
        │
        ▼
┌─────────────────┐
│  main.py        │  lifespan → 启动时建表
│  FastAPI app    │  include_router → 注册路由
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  api/router.py  │  总路由分发 → /v1/* 交给 v1_router
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  api/v1/user.py │  端点层 — 接收 HTTP 请求，参数解析，返回响应
│  @router.get()  │  职责：协议转换（HTTP ↔ Python）
└──┬──────────┬───┘
   │          │
   │ Depends(get_db)    ← 依赖注入，自动获取数据库会话
   │          │
   ▼          ▼
┌─────────────────┐     ┌──────────────────┐
│ schemas/user.py │     │ services/user.py │  业务逻辑层
│ 请求/响应校验    │     │ CRUD 函数         │  职责：数据操作
│ (Pydantic)      │     │ (纯 Python)       │
└─────────────────┘     └────────┬─────────┘
                                 │
                                 ▼
                         ┌──────────────┐
                         │ models/user.py│   ORM 模型层
                         │ class User    │   职责：表结构定义
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │ core/db.py    │   数据库连接层
                         │ engine        │   职责：连接池、会话管理
                         │ SessionLocal  │
                         │ Base          │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │   MySQL      │
                         │   数据库      │
                         └──────────────┘
```

---

## 3. 文件清单与职责

| 文件 | 所属层 | 职责 |
|------|--------|------|
| `config.py` | 配置 | 从环境变量读取数据库连接信息，拼成 `database_url` |
| `core/db.py` | 数据库 | 创建 `engine`（连接池）、`SessionLocal`（会话工厂）、`Base`（模型根）、`get_db`（依赖注入） |
| `models/__init__.py` | 模型 | 注册所有 ORM 模型，让 `Base.metadata` 能收录 |
| `models/user.py` | 模型 | 定义 `users` 表的 ORM 映射 |
| `schemas/user.py` | 校验 | 定义 API 的请求/响应数据结构（Pydantic） |
| `services/user.py` | 业务 | 实现 CRUD 操作（纯 Python，可独立测试） |
| `api/v1/user.py` | 接口 | REST 端点：`GET/POST/PATCH/DELETE /users` |
| `api/v1/router.py` | 路由 | 注册 v1 下所有模块的路由 |
| `api/router.py` | 路由 | 总路由，分发到各版本 |
| `main.py` | 入口 | 创建 FastAPI app，配置 lifespan 建表 |

---

## 4. 逐层解析

### 4.1 配置层：`config.py`

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "web-fastapi"
    debug: bool = True

    # ── 数据库连接配置：5 个字段拼出连接字符串 ──
    db_host: str = "127.0.0.1"     # 数据库 IP
    db_port: int = 3306            # MySQL 默认端口
    db_user: str = "root"          # 数据库用户名
    db_password: str = ""          # 密码（生产环境从 .env 读取）
    db_name: str = "local_data"    # 数据库名

    @property
    def database_url(self) -> str:
        """拼出 SQLAlchemy 连接字符串."""
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = {"env_file": ".env", "case_sensitive": False}

settings = Settings()
```

**数据流**：

```
.env 文件 ──┐
             ├──→ pydantic-settings 读取 ──→ Settings 实例
config.py 默认值 ──┘                         │
                                             │ database_url 属性
                                             ▼
                              "mysql+pymysql://root:root123@127.0.0.1:3306/local_data"
                                             │
                                             ▼ 被 core/db.py 引用
                                       create_engine(url)
```

**`.env` 文件**（覆盖默认值，不提交 Git）：

```env
db_password=
db_name=
```

---

### 4.2 数据库层：`core/db.py`

```python
# core/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings

# ── ① Engine（连接池）──
engine = create_engine(
    settings.database_url,  # "mysql+pymysql://root:...@127.0.0.1:3306/local_data"
    pool_size=10,           # 常驻连接数
    max_overflow=20,        # 峰值额外连接数（最大 30）
    pool_pre_ping=True,     # 拿连接前先 ping，避免断线
    connect_args={
        "server_public_key": None,  # MySQL 8.0 caching_sha2_password 认证
    },
)

# ── ② SessionLocal（会话工厂）──
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── ③ Base（ORM 模型根）──
class Base(DeclarativeBase):
    pass

# ── ④ get_db（FastAPI 依赖注入）──
def get_db():
    db = SessionLocal()
    try:
        yield db      # 请求进来 → 创建新会话
    finally:
        db.close()     # 请求结束 → 关闭会话
```

**四个核心对象的角色**：

| 对象 | 类型 | 生命周期 | 比喻 |
|------|------|---------|------|
| `engine` | `Engine` | 应用启动时创建一次，整个进程只有一个 | 电话总机 |
| `SessionLocal` | `sessionmaker` | 工厂函数，在模块加载时创建 | 接线员 |
| `Base` | `DeclarativeBase` | 类对象，所有模型的父类 | 户口本（记录谁是谁） |
| `get_db()` | 生成器函数 | 每个请求调用一次，yield → finally | 每次通话的接线员 |

---

### 4.3 模型层：`models/`

**`models/__init__.py`** — 注册中心：

```python
from app.core.db import Base       # 重导出，方便其他地方 from app.models import Base
from app.models.user import User   # 导入 User → Base.metadata 收录

__all__ = ["Base", "User"]
```

> **关键逻辑**：只有被 import 过的模型才会出现在 `Base.metadata.tables` 里，进而被 `create_all` 建表。每新增一个模型，必须在这里加一行 `from ... import ...`。

**`models/user.py`** — 表结构定义：

```python
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models import Base

class User(Base):
    __tablename__ = "users"     # 数据库表名

    # Mapped[int] = Python → SQL 类型映射
    # mapped_column(...) = 列约束
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), default=None)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

**隐式注入机制：`class User(Base)` 背后发生了什么**

你看到的建表逻辑没有任何显式的"注册"或"合并"——一切靠 `class User(Base)` 这一行隐式完成。

Python 执行 `class User(Base):` 时，不只是创建了一个普通的类。`DeclarativeBase` 内部有一个**元类（metaclass）**，它在类创建的那一刻拦截了整个过程：

```python
# 你写的代码：
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

# DeclarativeBase 的元类在背后做的事（简化）：
# ① Python 执行类体，收集所有属性
# ② 元类拦截，提取 __tablename__ → 注册表名
# ③ 元类提取 Mapped[...] → 注册列定义
# ④ 元类提取 mapped_column(...) → 注册约束
# ⑤ 自动添加到 Base.metadata.tables['users']
```

所以 `Base.metadata` 是一个**自动登记表**——不需要也不存在手动注册的代码：

```python
Base.metadata.register(User)  # ❌ 不存在这行代码，也不需要

# class User(Base) 执行完的那一刻就自动注册了：
print(Base.metadata.tables.keys())  # → dict_keys(['users'])
print(Base.metadata.tables['users'].columns.keys())
# → ['id', 'name', 'email', 'avatar_url', 'is_active', 'created_at', 'updated_at']
```

| 机制 | 说明 |
|------|------|
| 什么时候注册 | `class User(Base)` 类定义执行的那一刻，不是运行时调用函数 |
| 谁做的注册 | `DeclarativeBase` 的元类，类创建时自动提取表信息并存入 `metadata` |

**模型 → DDL 对应关系**：

```python
# Python 代码                         → 生成的 SQL DDL
class User(Base):                     # CREATE TABLE users (
    __tablename__ = "users"
                                       #
    id: Mapped[int]                    #   id INTEGER NOT NULL AUTO_INCREMENT,
    = mapped_column(primary_key=True,  #
                    autoincrement=True)#   PRIMARY KEY (id),
                                       #
    name: Mapped[str]                  #   name VARCHAR(100) NOT NULL,
    = mapped_column(String(100))       #
                                       #
    email: Mapped[str]                 #   email VARCHAR(200) NOT NULL UNIQUE,
    = mapped_column(String(200),       #
                    unique=True)       #
                                       #
    created_at: Mapped[datetime]       #   created_at DATETIME NOT NULL
    = mapped_column(DateTime(),        #     DEFAULT CURRENT_TIMESTAMP,
                    server_default=    #
                    func.now())        # )
```

---

### 4.4 数据校验层：`schemas/user.py`

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime

# ── 请求模型：定义"客户端必须传什么" ──
class UserCreate(BaseModel):
    name: str
    email: EmailStr              # Pydantic 自动校验邮箱格式，非法返回 422
    avatar_url: str | None = None

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    avatar_url: str | None = None
    is_active: bool | None = None   # 全部可选 = PATCH 语义

# ── 响应模型：定义"服务端返回什么" ──
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    avatar_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}  # ← ORM 对象可直接转 Pydantic
```

> **`from_attributes=True`** 是关键配置。它让 Pydantic 可以从 ORM 对象（`user.name`）而不是字典（`user["name"]`）中取值。endpoint 返回 ORM 对象时，FastAPI 用这个配置自动调用 `UserResponse.model_validate(user)`。

---

### 4.5 业务逻辑层：`services/user.py`

```python
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.errors import NotFoundError

# ── 查单条：按主键 ──
def get_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)       # 等价于 SELECT * FROM users WHERE id = ?
    if not user:
        raise NotFoundError(f"用户 ID={user_id} 不存在")
    return user

# ── 查多条：分页 + 排序 ──
def list_users(db: Session, page: int = 1, size: int = 20) -> list[User]:
    offset = (page - 1) * size
    return list(
        db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .limit(size).offset(offset)
        ).scalars().all()
    )

# ── 增 ──
def create_user(db: Session, name: str, email: str, avatar_url: str | None = None) -> User:
    user = User(name=name, email=email, avatar_url=avatar_url)
    db.add(user)         # ① 标记"这个对象要插入"
    db.commit()          # ② 真正执行 INSERT（事务提交）
    db.refresh(user)     # ③ 从数据库读回 server 端生成的值（id、时间戳）
    return user

# ── 改 ──
def update_user(db: Session, user_id: int, **kwargs) -> User:
    user = get_user(db, user_id)
    for field, value in kwargs.items():
        if value is not None:
            setattr(user, field, value)  # 动态修改属性
    db.commit()                           # SQLAlchemy 自动检测变化，只 UPDATE 改过的列
    db.refresh(user)                      # 拿回 updated_at 等数据库自动刷新的值
    return user

# ── 删 ──
def delete_user(db: Session, user_id: int) -> None:
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()
```

> **services 层不依赖 FastAPI** — 没有 `HTTPException`，没有 `Depends`，只有纯 Python。业务异常用自定义的 `NotFoundError`，由 endpoint 层决定怎么映射到 HTTP 状态码。

---

### 4.6 接口层：`api/v1/user.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.errors import NotFoundError
from app.services.user import create_user, delete_user, get_user, list_users, update_user

router = APIRouter()

@router.get("/users", response_model=list[UserResponse])
def list_users_api(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),     # ← FastAPI 自动注入数据库会话
):
    return list_users(db, page=page, size=size)

@router.post("/users", response_model=UserResponse, status_code=201)
def create_user_api(body: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, name=body.name, email=body.email, avatar_url=body.avatar_url)

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_api(user_id: int, db: Session = Depends(get_db)):
    try:
        return get_user(db, user_id)
    except NotFoundError as e:               # 业务异常 → HTTP 状态码
        raise HTTPException(status_code=404, detail=str(e))
```

**路由注册链路**：

```
main.py                    app.include_router(api_router, prefix="/api")
    ↓
api/router.py              api_router.include_router(v1_router, prefix="/v1")
    ↓
api/v1/router.py           router.include_router(user.router, tags=["user"])
    ↓
api/v1/user.py             @router.get("/users/{user_id}")
```

最终 URL：`GET /api/v1/users/{user_id}`

---

### 4.7 启动入口：`main.py`

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.router import api_router
from app.core.db import engine
from app.models import Base          # ← import 触发 models/__init__.py 注册所有模型

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ═══ 启动阶段 ═══
    Base.metadata.create_all(bind=engine)   # ← 建表
    yield                                    # ← 服务器运行中...
    # ═══ 停止阶段 ═══
    engine.dispose()                        # ← 释放连接池

app = FastAPI(title="web-fastapi", lifespan=lifespan)
app.include_router(api_router, prefix="/api")
```

---

## 5. 建表逻辑详解

### 5.1 建表语句在哪

```python
# main.py:18
Base.metadata.create_all(bind=engine)
```

### 5.2 `Base.metadata` 里有什么

`metadata` 是 SQLAlchemy 的"模型注册表"。每定义一个 `class Xxx(Base)`，SQLAlchemy 就把这个类的表结构信息记到 `Base.metadata` 里。

**触发条件**：模型类必须被 Python 解释器执行过（被 import 过），才会注册到 `metadata`。

```python
# models/__init__.py
from app.models.user import User  # ← 这一行执行后，User 被注册到 Base.metadata
```

验证：

```python
from app.models import Base
print(Base.metadata.tables.keys())  # → dict_keys(['users'])
```

### 5.3 `create_all` 实际发了什么 SQL

`create_all` 遍历 `metadata.tables`，给每个表发 `CREATE TABLE IF NOT EXISTS`。等价于：

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '用户名，用于展示和搜索',
    email VARCHAR(200) NOT NULL COMMENT '登录邮箱，全局唯一，用作登录凭证',
    avatar_url VARCHAR(500) NULL COMMENT '头像 URL，NULL 表示未设置',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '账户状态',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE (email)
);
```

**`IF NOT EXISTS`** — 表已存在就跳过，不会删数据，也不会改表结构。所以每次重启都调用 `create_all` 是安全的。

### 5.4 调用时机

```
uv run dev
  → main.py:start()
    → uvicorn.run("app.main:app")
      → FastAPI 实例化
        → lifespan 启动阶段
          → Base.metadata.create_all(bind=engine)  ← 此时建表
      → 开始接收 HTTP 请求
```

---

## 6. 完整请求追踪

以 `POST /api/v1/users` 创建一个用户为例，追踪数据流经的每一层：

```
客户端                          服务端 Python 代码                          MySQL
──────                          ────────────────                          ─────

① 发送 POST 请求
{"name":"张三",
 "email":"a@b.com"}

                                ② FastAPI 路由匹配
                                POST /api/v1/users
                                  → api/v1/user.py:create_user_api()

                                ③ Pydantic 校验请求体
                                UserCreate(name="张三", email="a@b.com")
                                  ├─ name: str ✓
                                  └─ email: 格式 ✓ → EmailStr

                                ④ FastAPI 依赖注入
                                db = SessionLocal()  → 创建数据库会话

                                ⑤ 调用 service
                                create_user(db, name="张三", email="a@b.com")

                                ⑥ 创建 ORM 对象
                                user = User(name="张三", email="a@b.com")

                                ⑦ 标记插入
                                db.add(user)
                                → SQLAlchemy 内部: pending insert

                                ⑧ 提交事务                                       ⑨ 数据库执行
                                db.commit()                                       INSERT INTO users
                                → 发出 INSERT SQL                               → (name, email)
                                                                                   VALUES ('张三', 'a@b.com')
                                ⑩ 刷新对象
                                db.refresh(user)                                  ⑪ 读回生成值
                                → SELECT ... WHERE id = LAST_INSERT_ID()         → id=1, created_at=...

                                ⑫ 返回 ORM 对象
                                return user

                                ⑬ Pydantic 序列化
                                UserResponse.model_validate(user)
                                → {"id":1, "name":"张三", ...}

⑭ 收到响应                      ← ⑭ FastAPI 返回 JSON
201 Created                      HTTP/1.1 201 Created
{"id":1,"name":"张三",          Content-Type: application/json
 "email":"a@b.com", ...}         body: {...}

                                ⑮ 请求结束
                                get_db() finally: db.close()
                                → 会话归还连接池
```

---

## 6.5 User 表在哪里"合并"——import 链与执行路径

没有一个显式的中心"调度器"去注册 User 表。**所有连接靠的是 Python 的 import 机制**。

### 6.5.1 Import 链：User 是如何在各个文件之间流转的

```
main.py:10
  from app.models import Base
        │
        │ 执行 → models/__init__.py
        │
        ▼
models/__init__.py:3-4
  from app.core.db import Base       ← 拿到 Base 类
  from app.models.user import User   ← 执行 → models/user.py
        │                                       │
        │                                       ▼
        │                              models/user.py:64
        │                                class User(Base):  ← User 类定义
        │                                  ...
        │                                User 被注册到 Base.metadata.tables
        │
        │ User 现在在 Base.metadata 里了
        │
        ▼
main.py:18  lifespan → Base.metadata.create_all(bind=engine)
                       ↑
                       此时 metadata.tables 里已经有 'users'
                       → 发出 CREATE TABLE IF NOT EXISTS users (...)
```

**启动时的完整 import 顺序**：

```
uv run dev
  → main.py 开始执行
    ① from app.models import Base
       ② models/__init__.py 执行
          ③ from app.core.db import Base
             ④ core/db.py 执行 → engine、SessionLocal、Base 类被创建
          ⑤ from app.models.user import User
             ⑥ models/user.py 执行 → class User(Base) 被定义
                → User 自动注册到 Base.metadata
       → main.py 拿到 Base 和 User
    ⑦ lifespan 启动 → Base.metadata.create_all(bind=engine)
       → 遍历 Base.metadata.tables = {'users'}
       → 发出 CREATE TABLE IF NOT EXISTS users (...)
```

### 6.5.2 请求时的执行路径：各层如何串联

以 `POST /api/v1/users` 为例：

```
HTTP 请求进入
        │
        ▼
api/v1/router.py:9
  from . import user                    ← ① 模块加载时 import
  router.include_router(user.router)    ← ② 注册 user 模块的路由
        │
        │ 路由匹配到 POST /api/v1/users
        ▼
api/v1/user.py:37-40
  def create_user_api(
      body: UserCreate,                 ← ③ Pydantic 校验请求体
      db: Session = Depends(get_db),    ← ④ FastAPI 调用 get_db() 注入 Session
  ):
      return create_user(db, ...)       ← ⑤ 调用 services/user.py
                    │
                    ▼
services/user.py:81-91
  def create_user(db, name, email, avatar_url):
      user = User(name=name, ...)       ← ⑥ 使用 models/user.py 的 User 类
      db.add(user)                      ← ⑦ SQLAlchemy 标记插入
      db.commit()                       ← ⑧ 发出 INSERT SQL
      db.refresh(user)                  ← ⑨ 读回数据库生成的值
      return user                       ← ⑩ 返回 ORM 对象
                    │
                    ▼ 回到 api/v1/user.py
FastAPI 看到 response_model=UserResponse
  → 自动调用 UserResponse.model_validate(user)   ← ⑪ ORM 对象 → Pydantic → JSON
  → 返回 HTTP 201 + JSON body
```

### 6.5.3 每个 import 的作用

| import 语句 | 文件 | 作用 |
|------------|------|------|
| `from app.models import Base` | `main.py:10` | **触发** models/__init__.py 执行，间接触发所有模型注册到 metadata |
| `from app.models.user import User` | `models/__init__.py:4` | **注册**：让 User 出现在 `Base.metadata.tables` 里，create_all 才能发现 |
| `from app.models.user import User` | `services/user.py:49` | **使用**：在 CRUD 函数中创建/查询/删除 User 对象 |
| `from app.schemas.user import UserCreate, UserResponse` | `api/v1/user.py:9` | **校验**：Pydantic 校验请求体和序列化响应 |
| `from app.services.user import create_user, ...` | `api/v1/user.py:11` | **调用**：endpoint 调用 service 函数 |
| `from app.api.deps import get_db` | `api/v1/user.py:8` | **注入**：FastAPI Depends() 给端点注入数据库会话 |

### 6.5.4 一句话总结

> 没有"合并"——**是 `models/__init__.py` 把 User 注册到 `Base.metadata`，`services/user.py` 直接用 User 类操作数据，`api/v1/user.py` 把 HTTP 请求路由到 service**。三条线各走各的，靠 Python import 和 FastAPI Depends 自动串联。

---

## 7. 添加新表的步骤

假设要新增一张 `posts` 表：

```
步骤               操作                                涉及文件
────────────────────────────────────────────────────────────────
1. 定义模型        class Post(Base):                   models/post.py
                   __tablename__ = "posts"
                   ...

2. 注册模型        from app.models.post import Post    models/__init__.py

3. 定义 Schema     PostCreate, PostResponse            schemas/post.py

4. 写业务逻辑      def create_post(db, ...)             services/post.py

5. 写端点          @router.post("/posts")               api/v1/post.py

6. 注册路由        router.include_router(post.router)   api/v1/router.py

7. 重启服务        uv run dev                          →
                   lifespan → create_all 自动建 posts 表
```

前三步是数据库相关的，后三步是 API 相关的，独立并行。
