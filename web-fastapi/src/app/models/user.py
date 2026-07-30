"""用户模型 — ORM 映射 users 表.

引入的 SQLAlchemy API 一览：

┌─ Mapped ────────────────────────────────────────────────────────┐
│ 类型标注，告诉 SQLAlchemy "这是一个数据库列，类型是 X"。        │
│                                                                 │
│   Mapped[int]     → 数据库 INTEGER                             │
│   Mapped[str]     → 数据库 VARCHAR                             │
│   Mapped[bool]    → 数据库 BOOLEAN                             │
│   Mapped[datetime] → 数据库 DATETIME                           │
│   Mapped[str | None] → 可空列（等价于 NULL 允许）               │
│                                                                 │
│ 这是 SQLAlchemy 2.0 新式写法，替代旧式 id = Column(Integer)。   │
│ Mapped 只回答 "是什么类型"，约束由 mapped_column 负责。         │
└────────────────────────────────────────────────────────────────┘
┌─ mapped_column ─────────────────────────────────────────────────┐
│ 定义列的约束和选项。每个参数对应数据库 DDL 中的一个概念：       │
│                                                                 │
│   primary_key=True     → PRIMARY KEY                            │
│   autoincrement=True   → AUTO_INCREMENT                         │
│   unique=True          → UNIQUE 约束                            │
│   default=True         → DEFAULT TRUE                           │
│   server_default=...   → 数据库端默认值（如 CURRENT_TIMESTAMP） │
│   onupdate=...         → ON UPDATE 触发器                       │
│   comment="..."        → 列注释                                 │
│                                                                 │
│ 注意 default vs server_default：                                │
│   default=...       — Python 层面提供默认值                     │
│   server_default=... — 数据库端 DDL 中写 DEFAULT，建表生效      │
└────────────────────────────────────────────────────────────────┘
┌─ DateTime ──────────────────────────────────────────────────────┐
│ sqlalchemy.DateTime — 告诉数据库这列是 DATETIME / TIMESTAMP。   │
│   DateTime(timezone=True):                                      │
│     MySQL      → TIMESTAMP（自带时区）                          │
│     PostgreSQL → TIMESTAMP WITH TIME ZONE                       │
│     SQLite     → 忽略（SQLite 不支持时区）                      │
│                                                                 │
│ 注意不要和 Python 的 datetime.datetime 混淆：                   │
│   from datetime import datetime          ← Python 类型          │
│   from sqlalchemy import DateTime         ← 数据库列类型         │
│   Mapped[datetime] = mapped_column(DateTime(...))               │
│          ↑ Python 类型               ↑ 数据库类型               │
└────────────────────────────────────────────────────────────────┘
┌─ func ──────────────────────────────────────────────────────────┐
│ 调用数据库内置函数。func.xxx() 相当于 SQL 里的 xxx()。           │
│                                                                 │
│   func.now()           → CURRENT_TIMESTAMP                      │
│   func.count(User.id)  → COUNT(users.id)                       │
│   func.coalesce(a, b)  → COALESCE(a, b)                        │
│                                                                 │
│ SQLAlchemy 不校验函数是否存在——写错了只会在数据库执行时报错。   │
└────────────────────────────────────────────────────────────────┘
"""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class User(Base):
    """用户表，存储系统用户的基本信息."""

    __tablename__ = "users"

    # ── 主键 ──
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="用户唯一 ID，数据库自增",
    )

    # ── 核心字段 ──
    name: Mapped[str] = mapped_column(
        String(100),  # MySQL VARCHAR 必须指定长度，不然 CompileError
        comment="用户名，用于展示和搜索",
    )
    email: Mapped[str] = mapped_column(
        String(200),  # 邮箱最长 254 字符，这里取 200 足够
        unique=True,
        comment="登录邮箱，全局唯一，用作登录凭证",
    )

    # ── 可选字段（允许 NULL，创建时可不传）──
    # 条件：类型标注 | None + default=None → 数据库字段为 NULLABLE
    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        default=None,        # Python 侧不传则为 None
        comment="头像 URL，NULL 表示未设置",
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,        # Python 侧不传则默认 True（非 NULL）
        comment="账户状态：True=启用，False=禁用",
    )

    # ── 时间戳（NOT NULL，但由数据库自动填入，创建时不需手动传）──
    # server_default=func.now() → 不传这列时，MySQL 用 CURRENT_TIMESTAMP 自动填入
    # 注意：类型是 datetime，不是 datetime | None，说明字段不允许 NULL
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # 数据库端自动填入，字段 NOT NULL
        comment="记录创建时间，数据库自动填入当前时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # 首次 INSERT 时数据库自动填入
        onupdate=func.now(),        # 每次 UPDATE 时数据库自动刷新
        comment="记录最后更新时间，每次 UPDATE 自动刷新",
    )
