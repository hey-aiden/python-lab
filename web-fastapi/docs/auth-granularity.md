# FastAPI 鉴权：三种粒度 & 完整对照

> 记录 FastAPI 中 `Depends()` 鉴权的三种粒度、写法、适用场景，以及当前项目的实现位置。

---

## 1. Cookie 操作：读取、设置、清除

### 1.1 读取 Cookie

在依赖函数中通过 `request.cookies` 读取（当前项目已使用）：

```python
# api/deps.py
from fastapi import Request

def verify_cookie(request: Request) -> dict:
    session = request.cookies.get("session")
    if not session:
        raise HTTPException(status_code=401, detail="未登录")
    return {"user_id": session}
```

FastAPI 也支持直接声明 `Cookie()` 参数（仅端点函数可用）：

```python
from fastapi import Cookie

@router.get("/profile")
def profile(session: str = Cookie()):
    return {"session": session}
```

| 读取方式 | 可用位置 | 说明 |
|----------|---------|------|
| `request.cookies.get("key")` | 任何地方（依赖函数、端点、中间件） | ✅ 当前项目使用 |
| `param: str = Cookie()` | 仅端点函数参数 | 直接拿到值，不需要 `request` |

### 1.2 设置 Cookie

FastAPI 设置 cookie 必须通过 `Response` 对象，不能在依赖函数中直接设置：

```python
from fastapi import Response

@router.post("/login")
def login(response: Response):
    # 设置 cookie
    response.set_cookie(
        key="session",
        value="user_abc123",
        httponly=True,     # JS 无法读取，防 XSS
        secure=True,       # 仅 HTTPS 传输
        samesite="lax",    # 跨站请求策略：lax / strict / none
        max_age=3600,      # 过期时间（秒），1 小时后失效
    )
    return {"msg": "登录成功"}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("session")  # 清除 cookie
    return {"msg": "已退出"}
```

### 1.3 登录接口完整示例

```python
# api/v1/auth.py
from fastapi import APIRouter, Response, HTTPException, Cookie

router = APIRouter()

# 硬编码的简易"数据库"
USERS = {"admin": "123456", "guest": "password"}

@router.post("/login")
def login(name: str, password: str, response: Response):
    """验证用户名密码，成功后写入 session cookie."""
    if name not in USERS or USERS[name] != password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    response.set_cookie(
        key="session",
        value=name,           # 实际项目应存 JWT 或 session id
        httponly=True,
        max_age=3600,
    )
    return {"msg": f"欢迎 {name}"}


@router.post("/logout")
def logout(response: Response):
    """清除 session cookie."""
    response.delete_cookie("session")
    return {"msg": "已退出"}


@router.get("/me")
def me(session: str = Cookie()):
    """读取当前登录用户."""
    if not session:
        raise HTTPException(status_code=401, detail="未登录")
    return {"user": session}
```

### 1.4 Cookie 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `key` | — | Cookie 名称 |
| `value` | — | Cookie 值 |
| `max_age` | — | 过期秒数（浏览器关闭即失效） |
| `expires` | — | 具体的过期时间戳 |
| `path` | `"/"` | Cookie 生效的路径 |
| `domain` | — | Cookie 生效的域名 |
| `secure` | `False` | 仅 HTTPS 传输（生产环境应设为 True） |
| `httponly` | `False` | JS 无法读取，防御 XSS |
| `samesite` | `"lax"` | 跨站策略：`lax`（默认）/ `strict`（最严）/ `none`（跨站，需 secure=True） |

### 1.5 鉴权流程总结

```
POST /login?name=admin&password=123456
  │
  ├─ 验证用户名密码
  ├─ response.set_cookie("session", "admin", httponly=True)
  └─ 返回 200

后续请求：
  │
  ├─ 浏览器自动携带 Cookie: session=admin
  ├─ router 级 dependencies 执行 verify_cookie()
  │     └─ request.cookies.get("session") → "admin"
  ├─ 端点函数执行
  └─ 返回数据

POST /logout
  │
  ├─ response.delete_cookie("session")
  └─ 返回 200
```

---

## 2. 三种粒度总览

```
app 级 ──── FastAPI(dependencies=[...])
  └─ router 级 ──── APIRouter(dependencies=[...])
       └─ 端点级 ──── @router.get(dependencies=[...])
            └─ 参数级 ──── def fn(user = Depends(...))  ← 可使用返回值
```

---

## 3. 各粒度详解

### 3.1 Router 级（当前项目使用）

适合：**某个版本 / 某个业务模块的所有端点都需要鉴权。**

```python
# api/v1/router.py
from fastapi import APIRouter, Depends
from app.api.deps import verify_cookie

router = APIRouter(dependencies=[Depends(verify_cookie)])
router.include_router(users.router, tags=["users"])
router.include_router(orders.router, tags=["orders"])
```

| 特点 | 说明 |
|------|------|
| 作用范围 | 该 router 下所有端点 |
| 能否拿到返回值 | ❌ 不能（依赖函数返回值被丢弃） |
| 如何跳过 | `@router.get("/health", dependencies=[])` 清空 |

> **项目当前就是这种**——`api/v1/router.py` 第 9 行。

---

### 3.2 App 级

适合：**全站鉴权，无一例外。**

```python
# main.py
from app.api.deps import verify_api_key

app = FastAPI(
    title="My API",
    dependencies=[Depends(verify_api_key)],  # 所有路由都执行
)
app.include_router(api_router, prefix="/api")
```

| 特点 | 说明 |
|------|------|
| 作用范围 | 所有路由（包括 `/docs`、`/openapi.json`） |
| 能否拿到返回值 | ❌ 不能 |
| 如何跳过 | 个别 router 无法跳过（除非在依赖函数内判断路径） |
| 慎用原因 | `/docs` 也受影响，访问 API 文档时需要带鉴权 |

> 一般不推荐用于鉴权，更适合记录全局日志、注入请求 ID 等轻量操作。

---

### 3.3 端点级

适合：**大部分端点公开，个别端点需要鉴权。**

```python
# api/v1/hello.py
from fastapi import APIRouter, Depends
from app.api.deps import verify_cookie

router = APIRouter()  # 不加 router 级依赖

@router.get("/hello")                           # ← 公开
def hello():
    return {"message": "hello"}

@router.get("/secret", dependencies=[Depends(verify_cookie)])  # ← 鉴权
def secret():
    return {"data": "sensitive"}
```

| 特点 | 说明 |
|------|------|
| 作用范围 | 仅该端点 |
| 能否拿到返回值 | ❌ 不能（写在 `dependencies=[]` 里的都取不到） |
| 适用场景 | 混合权限——少数需要鉴权，多数公开 |

---

### 3.4 参数级（可获取返回值）

适合：**端点需要用到鉴权后返回的用户信息。**

```python
# api/v1/hello.py
from fastapi import Depends
from app.api.deps import verify_cookie

@router.get("/profile")
def profile(user: dict = Depends(verify_cookie)):  # ← 可拿到 user dict
    return {"user_id": user["user_id"]}
```

| 特点 | 说明 |
|------|------|
| 作用范围 | 仅该端点 |
| 能否拿到返回值 | ✅ **能**——依赖函数 `return` 的值注入到参数 |
| 适用场景 | 端点需要当前用户 ID、角色、权限等 |

---

## 4. 四种方式对照

| 写法 | 作用范围 | 拿到返回值 | 跳过方式 |
|------|---------|-----------|---------|
| `app = FastAPI(dependencies=[...])` | 所有路由 | ❌ | 很难 |
| `router = APIRouter(dependencies=[...])` | 该 router | ❌ | `dependencies=[]` |
| `@router.get(dependencies=[...])` | 该端点 | ❌ | 不加即可 |
| `def fn(x = Depends(...))` | 该端点 | ✅ | 不加即可 |

---

## 5. 依赖函数写法

```python
# api/deps.py
from fastapi import HTTPException, Request

def verify_cookie(request: Request) -> dict:
    """读取 cookie，返回用户信息（注入到参数级 Depends 中）."""
    session = request.cookies.get("session")
    if not session:
        raise HTTPException(status_code=401, detail="未登录")
    return {"user_id": session}

def verify_admin(user: dict = Depends(verify_cookie)) -> dict:
    """链式依赖：先鉴权，再校验角色."""
    if user["user_id"] != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user
```

> `verify_admin` 依赖 `verify_cookie`——FastAPI 自动解析依赖链。

---

## 6. 混合示例

```python
# app 级：日志注入（轻量，无感）
app = FastAPI(dependencies=[Depends(inject_request_id)])

# router 级：v1 全部鉴权
api_router = APIRouter(dependencies=[Depends(verify_cookie)])

# 端点级异常：health 不鉴权
@api_router.get("/health", dependencies=[])
def health():
    return {"status": "ok"}

# 参数级：需要具体用户信息
@api_router.get("/profile")
def profile(user: dict = Depends(verify_cookie)):
    return {"user": user["user_id"]}
```

---

## 7. 当前项目状态

| 配置 | 位置 | 粒度 |
|------|------|------|
| `dependencies=[Depends(verify_cookie)]` | `api/v1/router.py:9` | Router 级 |
| `verify_cookie` | `api/deps.py` | 依赖函数 |

如需升级为混合模式（部分端点公开），在对应端点加 `dependencies=[]` 即可，不动其他地方。
