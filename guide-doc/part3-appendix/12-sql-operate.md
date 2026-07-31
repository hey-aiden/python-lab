# SQL 操作：原生 SQL vs ORM（SQLAlchemy）

> 📖 理解 ORM 的核心概念，以及如何用 Python 对象操作代替手写 SQL 字符串。

---

## 1. 先搞清楚：不用 ORM 怎么操作数据库

Python 标准库自带 `sqlite3`，第三方库 `pymysql` / `psycopg2` 提供 MySQL / PostgreSQL 驱动。它们都实现了 **DB-API 2.0** 规范，API 几乎一样。

### 原生 SQL 操作流程

```python
import pymysql

# 1. 建立连接
conn = pymysql.connect(host="localhost", user="root", password="", database="mydb")
cursor = conn.cursor()

# 2. 执行 SQL 字符串
cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (1,))
row = cursor.fetchone()
print(row[0], row[1], row[2])  # 靠下标取值 → 1, "张三", "zhang@example.com"

# 3. 插入
cursor.execute(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    ("李四", "li@example.com")
)
conn.commit()

# 4. 关闭
cursor.close()
conn.close()
```

**痛点很明显：**

| 问题 | 后果 |
|------|------|
| SQL 写成字符串 | 没有语法高亮、没有自动补全、拼错字段名查不出来 |
| `row[0]` `row[1]` 靠下标 | 表结构一改（加列/删列），下标全乱，很难排查 |
| 拼 SQL 字符串 | 忘了用参数化查询 → SQL 注入漏洞 |
| 连接管理 | 每次都手动 open/close，忘了关就泄漏 |

---

## 2. ORM 做了什么

**ORM（Object-Relational Mapper）做的事情就是：**

```
数据库          ←── ORM ──→      Python 代码
──────────────────────────────────────────────
表 (users)        ←→     类 (User)
列 (id, name)     ←→     属性 (user.id, user.name)
行 (1, "张三")     ←→     对象 (User(id=1, name="张三"))
SQL 查询          ←→     方法调用 (session.get(User, 1))
```

### 同一个操作，两边对比

```python
# ========== 原生 SQL ==========
cursor.execute("SELECT * FROM users WHERE id = %s", (1,))
row = cursor.fetchone()
name = row[1]                      # 下标，不知道第几个是什么

# ========== ORM ==========
user = session.get(User, 1)        # 传类 + 主键值
name = user.name                   # 直接 .属性名，IDE 有补全
```

---

## 3. 核心概念拆解

### 3.1 Model（模型类）= 表的定义

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """所有模型的基类 — 只需定义一次."""
    pass

class User(Base):
    __tablename__ = "users"              # 对应的表名

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
```

| 概念 | 对应数据库 |
|------|-----------|
| `class User(Base)` | `CREATE TABLE users (...)` |
| `__tablename__ = "users"` | 表名 |
| `Mapped[int]` | 列的类型（Python → SQL 映射） |
| `mapped_column(primary_key=True)` | `PRIMARY KEY` |
| `mapped_column(unique=True)` | `UNIQUE` 约束 |

### 3.2 Engine（引擎）= 数据库连接池

```python
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:@localhost:3306/mydb")
#                                          │       │  │   │   │
#                                         驱动    用户 密码 主机 端口/库名

# 等价于手写：
# conn = pymysql.connect(host="localhost", user="root", password="", database="mydb")
```

不需要每次手动 `connect()` / `close()`，Engine 内部管理一个连接池。

### 3.3 Session（会话）= 一次"对话"

```python
from sqlalchemy.orm import Session

session = Session(engine)

# 会话期间的所有操作是一个"工作单元"
user = session.get(User, 1)         # 查
user.name = "新名字"                 # 改
session.add(User(name="王五"))       # 增
session.delete(user)                 # 删
session.commit()                     # 一次性提交所有变更
```

用一个比喻理解：

```
Engine   = 电话总机（管着一堆电话线）
Session  = 一次通话（你拿起电话，说几句话，挂断）
commit() = "好的，就按刚才说的办"
```

---

## 4. 增删改查对照表

下面的例子都用同一个场景：`users` 表有 `id`、`name`、`email` 三个字段。

### 4.1 查询（SELECT）

```python
# ========== 查单条：按主键 ==========
# SQL:
cursor.execute("SELECT * FROM users WHERE id = %s", (1,))

# ORM:
user = session.get(User, 1)


# ========== 查单条：按条件 ==========
# SQL:
cursor.execute("SELECT * FROM users WHERE email = %s", ("a@b.com",))

# ORM:
user = session.execute(
    select(User).where(User.email == "a@b.com")
).scalar_one_or_none()


# ========== 查多条：全表 ==========
# SQL:
cursor.execute("SELECT * FROM users")

# ORM:
users = session.execute(select(User)).scalars().all()


# ========== 查多条：带条件 + 排序 + 分页 ==========
# SQL:
cursor.execute(
    "SELECT * FROM users WHERE name LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s",
    ("%张%", 10, 20)
)

# ORM:
users = session.execute(
    select(User)
    .where(User.name.like("%张%"))
    .order_by(User.id.desc())
    .limit(10).offset(20)
).scalars().all()


# ========== 只查某些列 ==========
# SQL:
cursor.execute("SELECT id, name FROM users")

# ORM:
rows = session.execute(
    select(User.id, User.name)
).all()
# → [(1, "张三"), (2, "李四"), ...]
```

### 4.2 插入（INSERT）

```python
# ========== 单条插入 ==========
# SQL:
cursor.execute(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    ("张三", "zhang@example.com")
)
conn.commit()

# ORM:
user = User(name="张三", email="zhang@example.com")
session.add(user)
session.commit()
# user.id 自动被填充（数据库生成的主键）


# ========== 批量插入 ==========
# SQL:
cursor.executemany(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    [("张三", "a@b.com"), ("李四", "c@d.com")]
)
conn.commit()

# ORM:
session.add_all([
    User(name="张三", email="a@b.com"),
    User(name="李四", email="c@d.com"),
])
session.commit()
```

### 4.3 更新（UPDATE）

```python
# ========== 查出来 → 改属性 → 提交 ==========
# SQL:
cursor.execute(
    "UPDATE users SET name = %s WHERE id = %s",
    ("新名字", 1)
)
conn.commit()

# ORM:
user = session.get(User, 1)
user.name = "新名字"
session.commit()
# flush() 时 SQLAlchemy 自动追踪哪些属性变了，只更新变化的列


# ========== 批量更新 ==========
# SQL:
cursor.execute(
    "UPDATE users SET name = %s WHERE name LIKE %s",
    ("已注销", "%test%")
)

# ORM:
session.execute(
    update(User)
    .where(User.name.like("%test%"))
    .values(name="已注销")
)
session.commit()
```

### 4.4 删除（DELETE）

```python
# ========== 删单条 ==========
# SQL:
cursor.execute("DELETE FROM users WHERE id = %s", (1,))

# ORM:
user = session.get(User, 1)
session.delete(user)
session.commit()


# ========== 批量删除 ==========
# SQL:
cursor.execute("DELETE FROM users WHERE name LIKE %s", ("%test%",))

# ORM:
session.execute(
    delete(User).where(User.name.like("%test%"))
)
session.commit()
```

---

## 5. 关联关系

### 5.1 表关联的本质

```sql
-- 两张表通过外键关联
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE posts (
    id INT PRIMARY KEY,
    title VARCHAR(200),
    user_id INT,                              -- 外键列
    FOREIGN KEY (user_id) REFERENCES users(id) -- 约束
);
```

### 5.2 ORM 中的写法

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    # relationship: 不是数据库列，是 Python 层面的"快捷方式"
    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # relationship: 反向引用
    author: Mapped["User"] = relationship(back_populates="posts")
```

### 5.3 关联查询对比

```python
# ========== JOIN 查询 ==========
# SQL:
cursor.execute("""
    SELECT u.name, p.title
    FROM users u
    JOIN posts p ON u.id = p.user_id
    WHERE u.id = %s
""", (1,))

# ORM:
user = session.execute(
    select(User).where(User.id == 1)
).scalar_one()

# 直接访问关联对象——SQLAlchemy 自动发 JOIN 查询
for post in user.posts:
    print(user.name, post.title)


# ========== 带关联的插入 ==========
# SQL（两张表分别插，保证外键值正确）:
cursor.execute("INSERT INTO users (name) VALUES (%s)", ("张三",))
user_id = cursor.lastrowid
cursor.execute(
    "INSERT INTO posts (title, user_id) VALUES (%s, %s)",
    ("我的第一篇", user_id)
)

# ORM（操作对象，自动处理外键）:
user = User(name="张三")
user.posts = [Post(title="我的第一篇"), Post(title="第二篇")]
session.add(user)
session.commit()  # 一次提交，自动插入 user + 两条 post，外键自动填
```

---

## 6. Alembic：表结构的版本管理

> Alembic 之于数据库，就像 Git 之于代码。

### 6.1 它解决了什么问题

| 没有 Alembic | 有 Alembic |
|-------------|-----------|
| 改字段靠脑子记，或者贴 Slack 里 | 每次变更生成一个迁移文件 |
| "生产库跑过 ALTER TABLE 没？"——不确定 | `alembic current` 一眼看出当前版本 |
| 新同事入职：dump SQL 手动导入 | `alembic upgrade head` 一条命令 |
| 回退靠备份恢复 | `alembic downgrade -1` 回退一步 |

### 6.2 工作流

```bash
# 1. 修改 ORM 模型（改 class User 的定义）
#    → 加了 age 字段，改了 email 的长度

# 2. 自动生成迁移文件
alembic revision --autogenerate -m "User 表加 age 字段，扩展 email 长度"
# → 生成 alembic/versions/a1b2c3d_user_加age.py

# 3. 检查生成的迁移文件（自动生成的不一定完美，要人工看一眼）

# 4. 应用到数据库
alembic upgrade head

# 5. 回退（如果需要）
alembic downgrade -1
```

### 6.3 迁移文件长什么样

```python
# alembic/versions/a1b2c3d_user_add_age.py
"""User 表加 age 字段，扩展 email 长度"""

def upgrade():
    op.add_column("users", sa.Column("age", sa.Integer(), nullable=True))
    op.alter_column("users", "email",
                    type_=sa.String(200), existing_type=sa.String(100))

def downgrade():
    op.drop_column("users", "age")
    op.alter_column("users", "email",
                    type_=sa.String(100), existing_type=sa.String(200))
```

两个核心概念：

| 概念 | 类比 | 说明 |
|------|------|------|
| `upgrade()` | 前进 | 把数据库更新到最新结构 |
| `downgrade()` | 回退 | 撤销这次变更（不是所有操作都能自动回退） |
| `alembic_version` 表 | Git HEAD | Alembic 自动在数据库里建的表，记录当前在哪个版本 |

---

## 7. 常见问题

### 7.1 ORM 性能不如原生 SQL？

**正确。但省掉的时间远大于性能损失。**

- 简单 CRUD：ORM 和手写 SQL 性能几乎一样（最终都转换成 SQL 执行）
- 复杂报表、大数据量：用原生 SQL 或 `session.execute(text("SQL"))` 兜底
- ORM 不是"不用 SQL"，而是"默认不用 SQL，需要时随时用"

```python
# 复杂查询可以用原生 SQL，还走同一个 session
from sqlalchemy import text
result = session.execute(text("SELECT ... 复杂的报表 SQL"))
```

### 7.2 `session.commit()` 和 `session.flush()` 的区别

| | `flush()` | `commit()` |
|---|----------|------------|
| 作用 | 把内存中的变更同步到数据库（发 SQL，但事务未提交） | 提交事务，写入永久生效 |
| 回滚 | 可以 `rollback()` | 不能回滚 |
| 拿到主键 | ✅ flush 后 `user.id` 就有值了 | ✅ |

```python
user = User(name="张三")
session.add(user)
session.flush()    # 发了 INSERT，但事务还没提交，user.id 已有值
# ... 做其他操作 ...
session.commit()   # 事务提交，修改永久生效
```

### 7.3 什么时候用 ORM，什么时候用原生 SQL？

```
用 ORM ────────────────────────────── 用原生 SQL
   │                                      │
   ├── 简单增删改查                       ├── 复杂多表关联报表
   ├── 单表或简单关联                     ├── 需要数据库特定语法
   ├── 表结构频繁变动                     ├── 大批量数据导入
   └── 团队协作，需要统一规范             └── 性能敏感的查询
```

---

## 本节要点

| # | 要点 |
|---|------|
| 1 | ORM 把**表→类、行→对象、列→属性**，操作 Python 对象就等于操作数据库 |
| 2 | `Base` 是所有模型的根，`Engine` 管连接池，`Session` 管一次对话 |
| 3 | 查：`session.get()` / `select()`；增：`session.add()`；改：直接改属性；删：`session.delete()` |
| 4 | `ForeignKey` 定义数据库外键约束，`relationship` 定义 Python 层面的便捷访问 |
| 5 | Alembic = 表结构的 Git，`upgrade head` 同步到最新，`downgrade -1` 回退一步 |
| 6 | `flush()` 发 SQL 但不提交事务，`commit()` 提交事务永久生效 |
| 7 | ORM 负责 90% 的 CRUD，复杂 SQL 用 `text()` 兜底，两者可以混用 |
