"""数据库引擎、会话工厂、Base 模型、get_db 依赖.

引入的 SQLAlchemy API 一览：

┌─ create_engine ─────────────────────────────────────────────────┐
│ 创建数据库连接池（"总机"），所有 SQL 最终通过它发出去。         │
│ 常用参数：                                                      │
│   pool_size=10     — 常驻连接数                                 │
│   max_overflow=20  — 峰值额外连接数，最大 = 10+20=30            │
│   pool_pre_ping=True — 拿连接前先 ping，避免用已断开的连接      │
└────────────────────────────────────────────────────────────────┘
┌─ sessionmaker ──────────────────────────────────────────────────┐
│ Session 工厂函数。每次 SessionLocal() 创建一个新的数据库会话。  │
│   autocommit=False — 必须显式 commit()，不会自动提交             │
│   autoflush=False  — 不自动 flush，手动控制何时发 SQL            │
│   bind=engine      — 产出的 Session 通过哪个 engine 连数据库    │
│                                                                 │
│ 比喻：                                                          │
│   Engine        = 电话总机（管着一堆电话线）                     │
│   SessionLocal  = 接线员（每次给你一条空闲线路）                 │
│   Session       = 一次通话（你拨号、说话、挂断）                 │
│   commit()      = "好的，就按刚才说的办"                        │
└────────────────────────────────────────────────────────────────┘
┌─ DeclarativeBase ───────────────────────────────────────────────┐
│ 所有 ORM 模型的"根"。每个表类继承 Base，SQLAlchemy 通过这个     │
│ 继承关系自动收集所有模型信息（表名、列、类型），用于建表和迁移。 │
│                                                                 │
│   Base                                                        │
│    ├── User  → users  表                                       │
│    ├── Post  → posts  表（以后加）                              │
│    └── ...                                                     │
└────────────────────────────────────────────────────────────────┘
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# ── Engine：数据库连接池（"总机"） ──
engine = create_engine(
    settings.database_url,
    pool_size=10,         # 常驻 10 个连接
    max_overflow=20,      # 高峰期最多再开 20 个，总共 30
    pool_pre_ping=True,   # 每次从池中取出连接前先 ping，避免使用已断开的连接
    connect_args={
        # MySQL 8.0 默认 caching_sha2_password 认证，PyMySQL 需要主动获取 RSA 公钥
        "server_public_key": None,  # None = 自动从服务端获取（安全）
    },
)

# ── SessionLocal：会话工厂（"接线员"），每次调用创建一个数据库会话 ──
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Base：所有 ORM 模型的根基类 ──
class Base(DeclarativeBase):
    """所有 ORM 模型的基类.

    每定义一个表类就继承它，SQLAlchemy 自动收集表结构信息。
    """

    pass


def get_db():
    """FastAPI 依赖注入：每个请求获取独立会话，请求结束后自动关闭.

    用法：
        @router.get("/users")
        def list_users(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
