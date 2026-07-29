# FastAPI 常见配置参考

> 以当前项目为对照，记录每个配置项的含义和使用位置。

---

## 1. FastAPI App 配置

创建应用实例时传入的参数。

```python
app = FastAPI(
    title="web-fastapi",          # API 标题，显示在 /docs 头部
    version="0.1.0",              # API 版本号
    description="描述",            # /docs 中的描述文字
    docs_url="/docs",             # Swagger UI 路径，None 则禁用
    redoc_url="/redoc",           # ReDoc 路径，None 则禁用
    openapi_url="/openapi.json",  # OpenAPI schema 路径
    dependencies=[...],           # 全局依赖，所有路由都执行
)
```

> **项目当前使用**: `title` + `version`

---

## 2. APIRouter 配置

```python
router = APIRouter(
    prefix="/v1",                 # 路径前缀，所有端点自动加上
    tags=["hello"],               # OpenAPI 文档分组标签（仅文档展示）
    dependencies=[Depends(...)],   # 路由级依赖，该 router 下所有端点都执行
    responses={404: {"description": "Not found"}},  # 公共响应文档
)
```

| 字段 | 类型 | 说明 | 当前项目 |
|------|------|------|---------|
| `prefix` | `str` | 路径前缀 | app 层面用 `include_router(prefix="/api")` 替代 |
| `tags` | `list[str]` | Swagger UI 分组名，纯展示 | ✅ 使用中 |
| `dependencies` | `list[Depends]` | 路由级依赖注入 | ✅ 使用中（cookie 鉴权） |
| `responses` | `dict` | 公共响应文档 | 未使用 |

> **项目当前使用**: `dependencies` + `tags`

---

## 3. include_router 配置

`app.include_router(router, ...)` 或嵌套 router 时用。

```python
app.include_router(
    router,
    prefix="/api",                # 给子路由加前缀
    tags=["v1"],                  # 覆盖子路由的 tags
    dependencies=[Depends(...)],  # 额外依赖，但只对该 router 生效
)
```

> **项目当前使用**: `prefix`（`/api`、`/v1` 两级拆分）

---

## 4. 路径操作装饰器

```python
@router.get("/path/{id}")
@router.post("/path")
@router.put("/path/{id}")
@router.delete("/path/{id}")
@router.patch("/path/{id}")
```

每个装饰器的常见参数：

```python
@router.get(
    "/users/{user_id}",
    response_model=UserResponse,  # 响应模型（FastAPI 自动校验 + 文档）
    status_code=201,              # 成功时的 HTTP 状态码，默认 200
    tags=["users"],               # 端点级别覆盖 tags
    summary="创建用户",            # /docs 中的简短描述
    description="详细说明",        # /docs 中的详细说明
    deprecated=True,              # 标记为已弃用
    dependencies=[Depends(...)],  # 端点级依赖
    responses={
        404: {"description": "用户不存在"},
        422: {"description": "参数校验失败"},
    },
)
```

| 字段 | 说明 | 当前项目 |
|------|------|---------|
| `response_model` | Pydantic 模型，自动校验响应 | ✅ 使用中 |
| `status_code` | 默认 200，创建资源通常用 201 | 未使用 |
| `tags` | 覆盖 tags，不用在 `include_router` 里写 | ✅ 使用中 |
| `dependencies` | 端点级依赖，或 `dependencies=[]` 清空上级依赖 | 未使用 |

> **项目当前使用**: `response_model`

---

## 5. 参数类型速查

FastAPI 根据参数类型自动推断数据来源。

### 路径参数

```python
@router.get("/{item_id}")
def hello(item_id: str):        # 路径中 {} 括起来的同名参数
    ...

# 请求: GET /ahah     → item_id = "ahah"
```

#### 路径参数类型转换器

| 写法 | 匹配范围 | 示例 URL | 结果 |
|------|---------|---------|------|
| `{id}` | 单段（默认） | `/files/abc` | `id = "abc"` |
| `{id:int}` | 单段 + 类型校验 | `/users/42` | `id = 42` |
| `{path:path}` | 多段（含 `/`） | `/files/a/b/c` | `path = "a/b/c"` |

```python
# :int —  只匹配数字，非数字自动返回 422
@router.get("/users/{user_id:int}")
def get_user(user_id: int):
    ...
# GET /users/42   → user_id = 42
# GET /users/abc  → 422（自动校验）

# :path —  匹配嵌套路径（含 /），必须放在路径末尾
@router.get("/files/{file_path:path}")
def get_file(file_path: str):
    ...
# GET /files/a/b/c.txt  → file_path = "a/b/c.txt"
```

> ⚠️ `:path` 会吞掉后续所有 `/`，必须放在路径末尾。写成 `/files/{path:path}/download` 则 `download` 被当成 path 的一部分，永远不会匹配。`<option value="int">` 和 `:path` 也可同时用 `Python type hint` 声明类型（如 `user_id: int`），FastAPI 自动校验。

### 查询参数

```python
@router.get("/search")
def search(q: str = "",         # URL ?q=xxx，有默认值 = 可选
           page: int = 1):      # URL ?page=1
    ...

# 请求: GET /search?q=hello&page=2
```

### 请求体

```python
@router.post("/user")
def create(body: UserCreate):   # Pydantic 模型 → JSON body

@router.post("/say_hi")
def say(msg: str = Body(embed=True)):  # 简单类型 + Body() → JSON body
    ...

# 请求: POST .../say_hi  Body: {"msg": "world"}
```

### 表单

```python
from fastapi import Form, File, UploadFile

@router.post("/login")
def login(username: str = Form(),       # form-data
          file: UploadFile = File()):   # 文件上传
    ...
```

### 请求头 / Cookie

```python
from fastapi import Header, Cookie

@router.get("/info")
def info(user_agent: str = Header(),    # 读取请求头 User-Agent
         session: str = Cookie()):      # 读取 cookie 中的 session 字段
    ...
```

| 来源 | 写法 | Content-Type |
|------|------|-------------|
| 路径 | `item_id: str` | — |
| 嵌套路径 | `file_path: str`（路由用 `{file_path:path}`） | — |
| 查询字符串 | `q: str = ""` | — |
| JSON body | `body: PydanticModel` | `application/json` |
| JSON body（内嵌） | `msg: str = Body(embed=True)` | `application/json` |
| 表单 | `msg: str = Form()` | `multipart/form-data` |
| 文件 | `file: UploadFile` | `multipart/form-data` |
| 请求头 | `ua: str = Header()` | — |
| Cookie | `session: str = Cookie()` | — |

### 分层原则：参数解析留在 Router 层

`Body()`、`Form()`、`Query()`、`Cookie()`、`Header()` 这些是 **HTTP 传输层概念**，只能在 Router 层出现，**绝不能**传入 Service 层。

```
Router 层（负责"怎么拿到数据"）     Service 层（负责"拿数据做什么"）
─────────────────────────────────   ─────────────────────────────
Form() / Body() / Query()  解析    纯 Python dict / Pydantic 模型
         ↓                                ↓
  转为 dict 或 Pydantic 传下去     只处理 Python 对象，不碰 HTTP
```

```python
# ✅ 正确：Router 解析 Form → 转 dict → Service 处理
@router.post("/get_form")
def getForm(user_name: str = Form()):
    return get_form({"user_name": user_name})   # ← 转成 dict

# service 层
def get_form(data: dict) -> dict:
    return {"user_name": data.get("user_name", "")}

# ❌ 错误：Form() 出现在 Service 层
def get_form(user_name: str = Form()):          # Service 依赖了 FastAPI
    ...
```

> **核心原则：Service 不 import FastAPI。** 这样 Service 可以脱离 HTTP 被任何地方复用——CLI、gRPC、脚本、测试。

---

## 6. 依赖注入 (Depends)

```python
# 可以放在这些位置：
app = FastAPI(dependencies=[...])         # 全局
router = APIRouter(dependencies=[...])     # 路由级
@router.get("/", dependencies=[...])       # 端点级
def fn(user: dict = Depends(get_user))    # 函数参数级（可获取返回值）

# 依赖函数写法
def verify(request: Request):
    cookie = request.cookies.get("session")
    if not cookie:
        raise HTTPException(401, detail="未登录")
    return {"user_id": cookie}   # 返回的值注入到端点函数
```

| 级别 | 作用范围 | 能拿到返回值？ |
|------|---------|--------------|
| `app` 级 | 所有路由 | ❌ |
| `router` 级 | 该路由下所有端点 | ❌ |
| 端点级 `[]` | 该端点 | ❌ |
| `Depends()` 参数 | 该端点 | ✅ |



## 7. 中间件

```python
@app.middleware("http")
async def middleware(request: Request, call_next):
    # call_next 之前 — 请求进入
    response = await call_next(request)   # 分界线
    # call_next 之后 — 响应返回
    return response
```

| 用途 | 说明 |
|------|------|
| 日志 | ✅ 当前项目使用 |
| CORS | 推荐 `CORSMiddleware` |
| 限流 | 基于 IP/用户 |
| 请求 ID | 注入 `X-Request-ID` |

> **项目当前使用**: 请求耗时日志

---

## 8. CORS 配置（待添加）

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许的前端域名
    allow_credentials=True,                    # 允许携带 cookie
    allow_methods=["GET", "POST"],            # 允许的 HTTP 方法
    allow_headers=["*"],                      # 允许的请求头
)
```

> 也放在 `setup_middleware()` 中统一注册。

---

## 9. 当前项目配置映射

| 配置项 | 位置 | 值 |
|--------|------|-----|
| `title` | `main.py` | `"web-fastapi"` |
| `version` | `main.py` | `"0.1.0"` |
| 全局依赖 | `api/v1/router.py` | `dependencies=[Depends(verify_cookie)]` |
| 路由前缀 | `main.py` → `api/router.py` | `/api` → `/v1` |
| tags | `api/v1/router.py` | `["hello"]` |
| `response_model` | `api/v1/hello.py` | ✅ 使用中 |
| `Body(embed=True)` | `api/v1/hello.py` | ✅ 使用中 |
| middleware | `core/middleware.py` | 请求耗时日志 |
| logging | `main.py` | `basicConfig` → `logs/app.log` |
