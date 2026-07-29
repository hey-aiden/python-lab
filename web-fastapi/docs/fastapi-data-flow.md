# FastAPI 框架设计原理与请求数据流

> 从原始 HTTP 请求到业务代码，数据经历了什么？FastAPI 和 Pydantic 各自做了什么？

---

## 1. 设计哲学：声明式 vs 命令式

FastAPI 的核心设计思想：**你声明"要什么"，框架负责"怎么拿"。**

```python
# 你只声明期望的数据形状
@router.post("/items")
def create(
    item_id: int,                     # 我要一个 int
    body: RequestContent,              # 我要一个符合 RequestContent 的对象
    session: str = Cookie(),           # 我要 cookie 里的 session
):
    ...

# FastAPI 自动完成：
# - 从路径提取 item_id，校验是不是 int
# - 从 JSON body 解析并校验是否符合 RequestContent
# - 从 Cookie 提取 session
# - 任何一个环节失败 → 返回 422/401，函数根本不会被调用
```

这和传统手动解析的对比：

```python
# ❌ 传统方式：你自己一步步取、转、验
def create(request):
    item_id = request.path_params.get("item_id")
    try:
        item_id = int(item_id)
    except (TypeError, ValueError):
        return 422
    body = json.loads(request.body)
    if "name" not in body:
        return 422
    name = body["name"]
    if not isinstance(name, str):
        return 422
    ...

# ✅ FastAPI：一行声明，框架搞定
def create(item_id: int, body: RequestContent):
    ...
```

---

## 2. 完整请求链路

一个 POST 请求从网卡到业务代码，经过 7 个阶段：

```
┌─────────────────────────────────────────────────────────────────┐
│ 原始 HTTP 请求                                                    │
│ POST /api/v1/items?source=web HTTP/1.1                          │
│ Cookie: session=abc123                                          │
│ {"name": "widget", "price": 9.99, "tax": 0.99}                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. ASGI 服务器（Uvicorn）                                         │
│    - 解析 TCP 字节流 → HTTP Request 对象                           │
│    - 构建 scope: {type, method, path, headers, ...}              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Starlette（FastAPI 底层）                                      │
│    - 路由匹配：POST /api/v1/items → checkReq()                    │
│    - 中间件执行：log_request_time 进门                             │
│    - 提取原始数据：                                                │
│      path_params = {"item_id": "42"}                             │
│      query_params = {"source": "web"}                            │
│      headers = {"cookie": "session=abc123", ...}                 │
│      body = b'{"name":"widget","price":9.99,"tax":0.99}'        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. FastAPI 依赖分析引擎（get_dependant）                            │
│    - 检查函数签名：checkReq(RequestContent, Annotated[str, Cookie])│
│    - 分析每个参数：                                                │
│      body: RequestContent  → Pydantic 模型 → 来源：JSON body       │
│      session: Cookie()    → 简单类型   → 来源：Cookie              │
│    - 构建依赖树（含 router 级 dependencies）                        │
│    - 确定执行顺序：verify_cookie → body 解析 → 端点函数              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Pydantic 校验 & 转换                                           │
│    - body 部分：                                                  │
│      raw_json = b'{"name":"widget","price":9.99}'               │
│           │                                                      │
│           ▼                                                      │
│      Pydantic 校验：                                              │
│        name: str     → "widget"      ✅ 是 str                    │
│        price: float  → 9.99          ✅ 是 float                  │
│        tax: float    → None（没传）   ✅ 可选，默认 None             │
│        description   → None（没传）   ✅ 可选，默认 None            │
│           │                                                      │
│           ▼                                                      │
│      result = RequestContent(name="widget", price=9.99)          │
│                                                                  │
│      如果 name 是数字 42 → Pydantic 抛 ValidationError             │
│      如果缺少 price     → Pydantic 抛 ValidationError             │
│                                                                  │
│    - Cookie 部分：                                                │
│      raw_cookies = {"session": "abc123"}                         │
│           │                                                      │
│           ▼                                                      │
│      Cookie() 提取 "session" → "abc123"                          │
│                                                                  │
│    - Path 部分：                                                  │
│      raw_path = {"item_id": "42"}                                │
│           │                                                      │
│           ▼                                                      │
│      int("42") → 42                                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. 异常拦截（校验失败时）                                           │
│                                                                  │
│    Pydantic ValidationError 或 HTTPException                     │
│           │                                                      │
│           ▼                                                      │
│    FastAPI 异常处理器                                             │
│           │                                                      │
│           ▼                                                      │
│    HTTP 422 / 401 / 404 → 返回给客户端，端点函数不执行                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. 端点函数执行（校验全部通过后才到这里）                               │
│                                                                  │
│    def checkReq(body: RequestContent, session: str | None):      │
│        # body.name    → "widget"  （已经是 str，不可能是 int）     │
│        # body.price   → 9.99      （已经是 float）               │
│        # session      → "abc123"  （已经是 str | None）           │
│                                                                  │
│        body.session_id = session  ← 纯粹的业务逻辑                  │
│        return body                                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. 响应处理                                                       │
│    - response_model=RequestContent → 输出也经过 Pydantic 校验      │
│    - 中间件执行：log_request_time 出门                             │
│    - 序列化为 JSON → HTTP Response                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Pydantic 的角色：三道防线

Pydantic 在整个请求链路中承担三个角色：

```
输入校验                     数据传输                   输出校验
───────                     ────────                   ───────
JSON / Form / Query   →    BaseModel 实例   →    response_model
  │                           │                       │
  │ ① 类型转换 + 校验          │ ② 类型安全的         │ ③ 过滤多余字段
  │    "42" → 42              │    . 访问              │    校验输出格式
  │    "true" → True          │    IDE 自动补全         │
  │    缺字段 → 422           │    重构安全            │
```

### 防线 1：输入校验（请求 → Router）

发生在阶段 4，由 Pydantic 根据 schema 自动执行：

```python
class RequestContent(BaseModel):
    name: str              # 必填，必须是 str
    price: float           # 必填，必须是 float
    tax: float | None = None  # 可选

# 收到 {"name": 42, "price": "9.99"}
# Pydantic:
#   name: 42      → 尝试 str(42) → "42"（宽松模式）或直接 422（严格模式）
#   price: "9.99" → float("9.99") → 9.99 ✅
```

### 防线 2：类型安全的数据传输（Router → Service → 返回）

校验通过后，`body` 就是一个**类型确定的 Pydantic 实例**：

```python
body.name         # IDE 知道这是 str
body.price        # IDE 知道这是 float
body.tax          # IDE 知道这是 float | None
body.model_dump() # → {"name": "widget", "price": 9.99, "tax": None}
```

在函数内部操作时，Pyright/Mypy 能实时检查类型错误，重构改名时自动更新所有引用。

### 防线 3：输出校验（返回 → 响应）

```python
@router.post("/items", response_model=RequestContent)
def create(body: RequestContent):
    body.extra_field = "oops"  # ← 不在 schema 中的字段
    return body
    # FastAPI: 输出时自动过滤掉 extra_field，响应中不会出现
```

同时校验输出类型——如果你的代码不小心把 `body.name` 赋值为 `int`，返回时 Pydantic 会报错（而不是把错误数据发给客户端）。

---

## 4. Service 层的边界：FastAPI 到此为止

这是整个设计中最关键的架构决策：

```
Router 层（依赖 FastAPI）          Service 层（纯 Python）
─────────────────────────         ─────────────────────
from fastapi import ...            import 只来自标准库或第三方
@router.get/post/...              普通函数
Form() Body() Cookie() Query()    只收 dict / Pydantic / 基本类型
raise HTTPException               raise 自定义业务异常
return dict/Pydantic               return dict/Pydantic
```

```python
# ✅ Service 层 — 完全不知道 HTTP 的存在
def get_greeting(item_id: str) -> dict:
    if item_id == "0":
        raise NotFoundError(f"item_id={item_id} 不存在")
    return {"message": f"Hello {item_id}"}

# 可以在任何环境调用：
get_greeting("42")           # FastAPI 中
get_greeting("42")           # CLI 脚本中
get_greeting("42")           # pytest 中（不需要 TestClient）
```

这条边界的价值：

| 能力 | 说明 |
|------|------|
| **独立测试** | Service 不需要 TestClient，直接 `assert get_greeting("42") == {...}` |
| **框架无关** | 换 Flask、gRPC、CLI，Service 一行不改 |
| **类型安全** | Pydantic 模型贯穿输入→处理→输出，类型检查全覆盖 |
| **可读性** | 看 Service 就知道业务逻辑，不被 HTTP 细节干扰 |

---

## 5. 总结

FastAPI 把请求处理分成三个世界和两个边界：

```
HTTP 世界              边界 1          Python 世界         边界 2         HTTP 世界
─────────           ──────────        ──────────        ──────────        ─────────
原始请求            FastAPI +         纯 Python           FastAPI +          JSON 响应
TCP 字节            Pydantic          业务逻辑            Pydantic
                   校验 + 转换                           过滤 + 序列化

                   Form() Body()      Service 层         response_model
                   Cookie() Query()   errors.py          自动文档
                   422 自动拦截       不依赖 FastAPI      字段过滤
```

**你只需要做两件事：**
1. 用 Pydantic 声明期望的字段（`BaseModel`）
2. 写 Service 处理纯 Python 对象

框架搞定剩下的一切——提取、转换、校验、文档、异常拦截。
