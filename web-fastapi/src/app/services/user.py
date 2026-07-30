"""用户业务逻辑 — 纯 Python，不依赖 FastAPI，可独立测试.

引入的 SQLAlchemy API 一览：

┌─ Session ───────────────────────────────────────────────────────┐
│ 类型标注，告诉 IDE "db 参数是一个 SQLAlchemy 会话对象"。        │
│                                                                 │
│   实际对象由 SessionLocal() 创建，Session 只是类型标注。        │
│                                                                 │
│   sessionmaker → 生产 Session 实例（工厂函数）                   │
│   Session      → 描述 Session 类型（类型标注）                   │
│                                                                 │
│ Session 常用方法：                                              │
│   db.get(Model, pk)     — 按主键查，最常用                      │
│   db.add(obj)           — 标记对象待插入                        │
│   db.delete(obj)        — 标记对象待删除                        │
│   db.execute(stmt)      — 执行任意 SQL（select/update/delete）   │
│   db.commit()           — 提交事务                              │
│   db.refresh(obj)       — 从数据库重新读取对象（拿到 server 端   │
│                           生成的值，如自增 id、默认时间戳）      │
│                                                                 │
│ 比喻：                                                          │
│   Session = 一次通话（拿起电话，说几句，commit = 挂断确认）      │
│   add/delete = 你说的话，commit 之前对方没当真                   │
│   commit()  = "好的，就按刚才说的办"——对方开始执行              │
└────────────────────────────────────────────────────────────────┘
┌─ select ────────────────────────────────────────────────────────┐
│ 用 Python 表达式构建 SELECT 语句，代替手写 SQL 字符串。          │
│                                                                 │
│   select(User)                          → SELECT * FROM users   │
│   select(User).where(User.name == "张三") → ... WHERE name='张三' │
│   select(User).order_by(User.id.desc()) → ... ORDER BY id DESC │
│   select(User).limit(20).offset(10)     → ... LIMIT 20 OFFSET 10│
│                                                                 │
│ select() 返回 Select 对象，调用 db.execute() 才真正发 SQL。     │
│ 用 .where() / .order_by() 等方法链式组合条件。                  │
│                                                                 │
│ 对比手写 SQL：                                                  │
│   ❌ "SELECT * FROM users WHERE name = '张三'"   — 字符串，     │
│      拼错字段名要到运行时才知道                                │
│   ✅ select(User).where(User.name == "张三")    — Python 表达式，│
│      IDE 能补全、重构工具能追踪、拼错即时报错                  │
└────────────────────────────────────────────────────────────────┘
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.errors import NotFoundError


def get_user(db: Session, user_id: int) -> User:
    """按 ID 查询单个用户，不存在抛 NotFoundError.

    db.get() 是按主键查询的最快方式——直接走主键索引。
    """
    user = db.get(User, user_id)
    if not user:
        raise NotFoundError(f"用户 ID={user_id} 不存在")
    return user


def list_users(db: Session, page: int = 1, size: int = 20) -> list[User]:
    """分页查询用户列表，按创建时间倒序.

    select() 构建查询 → .where() 条件 → .order_by() 排序 → .limit/.offset 分页
    最终 db.execute() 发出 SQL。
    """
    offset = (page - 1) * size
    return list(
        db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .limit(size)
            .offset(offset)
        ).scalars().all()
    )


def create_user(db: Session, name: str, email: str, avatar_url: str | None = None) -> User:
    """创建用户，返回创建后的 User 对象（含自增 id）.

    db.add() 只是标记"这个对象要插入"，db.commit() 才真正发 INSERT。
    db.refresh() 重新从数据库读取，拿到 server_default 生成的值（时间戳等）。
    """
    user = User(name=name, email=email, avatar_url=avatar_url)
    db.add(user)          # 标记待插入
    db.commit()           # 真正执行 INSERT
    db.refresh(user)      # 拿回数据库生成的值（created_at 等）
    return user


def update_user(db: Session, user_id: int, **kwargs) -> User:
    """按 ID 更新用户，只更新传了值的字段（PATCH 语义）.

    SQLAlchemy 自动追踪对象属性的变化——改了哪个属性，commit 时只 UPDATE 那个列。
    setattr(user, field, value) 动态设置属性，等价于 user.name = "新名字"。
    """
    user = get_user(db, user_id)
    changed = False
    for field, value in kwargs.items():
        if value is not None:
            setattr(user, field, value)  # 等价于 user.xxx = value
            changed = True
    if changed:
        db.commit()        # SQLAlchemy 自动检测哪些属性变了，只更新变化的列
        db.refresh(user)   # 拿回 updated_at 等数据库端自动刷新的值
    return user


def delete_user(db: Session, user_id: int) -> None:
    """按 ID 删除用户，不存在抛 NotFoundError.

    db.delete() 标记对象待删除，commit() 真正执行 DELETE。
    """
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()
