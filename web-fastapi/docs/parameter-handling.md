# FastAPI 参数处理：自动匹配规则

> FastAPI 如何根据参数类型和名字自动推断数据来源、类型转换和校验。

---

## 1. 核心规则：一条公式

```
参数的类型注解 + 参数名 + 默认值 → FastAPI 自动推断来源 + 校验 + 文档
```

---

## 2. 六种来源的自动匹配

### 2.1 路径参数 — 匹配 `{}` 中的同名变量

```python
@router.get("/users/{user_id}/posts/{post_id}")
def get_post(user_id: int, post_id: str):
    ...

# GET /users/42/posts/hello  →  user_id=42(int), post_id="hello"(str)
```

| 规则 | 说明 |
|------|------|
| 匹配来源 | URL 路径中 `{name}` 里的 name |
| 必须同名 | ✅ 参数名必须和 `{xxx}` 一致 |
| 类型转换 | `user_id: int` 自动把 `"42"` 转成 `42` |

---

### 2.2 查询参数 — 匹配 `?key=value` 中的 key

```python
@router.get("/search")
def search(q: str, page: int = 1, sort: str = "new"):
    ...

# GET /search?q=hello&page=2  →  q="hello", page=2, sort="new"(默认值)
```

| 规则 | 说明 |
|------|------|
| 匹配来源 | URL `?key=value` 中的 key |
| 同名匹配 | ✅ 参数名 = query key |
| 可选 | 有默认值 → 可选；无默认值 → 必填 |
| 别名 | `q: str = Query(alias="query")` → 参数名 `q`，URL 用 `?query=xxx` |

---

### 2.3 JSON Body — 匹配模型的字段名

```python
class UserCreate(BaseModel):
    name: str
    age: int

@router.post("/users")
def create(body: UserCreate):
    ...

# POST {"name": "aiden", "age": 25}  →  body.name="aiden", body.age=25
```

| 规则 | 说明 |
|------|------|
| 匹配来源 | JSON body 中的 key |
| 字段名匹配 | ✅ Pydantic 字段名 = JSON key |
| 简单类型 | `msg: str = Body(embed=True)` → JSON `{"msg": "hello"}` 中的 `msg` |

---

### 2.4 Form 数据 — 匹配 form 字段名

```python
@router.post("/login")
def login(user_name: str = Form(), password: str = Form()):
    ...

# POST user_name=aiden&password=123  →  user_name="aiden", password="123"
```

| 规则 | 说明 |
|------|------|
| 匹配来源 | `application/x-www-form-urlencoded` 或 `multipart/form-data` |
| 同名匹配 | ✅ 参数名 = form 字段名 |
| 别名 | `nickname: str = Form(alias="user_name")` → 参数名 `nickname`，form 中用 `user_name` |
| 可选 | `bio: str = Form(default="")` → form 没传就用 `""` |
| 文件 | `file: UploadFile = File()` → 文件上传 |

---

### 2.5 Cookie — 匹配 cookie 名

```python
@router.get("/profile")
def profile(session: str = Cookie()):
    ...

# Cookie: session=abc123  →  session="abc123"
```

| 规则 | 说明 |
|------|------|
| 匹配来源 | 请求头 `Cookie:` 中的键值对 |
| 同名匹配 | ✅ 参数名 = cookie 名 |

---

### 2.6 请求头 — 匹配 header 名

```python
@router.get("/info")
def info(user_agent: str = Header(), host: str = Header()):
    ...

# Header: User-Agent: Mozilla/5.0  →  user_agent="Mozilla/5.0"
# Header: Host: example.com         →  host="example.com"
```

| 规则 | 说明 |
|------|------|
| 匹配来源 | HTTP 请求头 |
| 命名转换 | Python `user_agent` 自动匹配 `User-Agent`（下划线 ↔ 连字符自动转换） |
| 别名 | `ua: str = Header(alias="User-Agent")` |

---

## 3. 类型转换 + 校验

FastAPI 自动根据类型注解做转换和校验：

```python
@router.get("/items/{item_id}")
def get_item(
    item_id: int,              # "42" 自动 → 42，传 "abc" → 422
    q: str = "",               # 始终是 str
    price: float = 0.0,        # "9.99" 自动 → 9.99
    active: bool = True,       # "true"/"1"/"yes" → True, "false"/"0"/"no" → False
    tags: list[str] = [],      # ?tags=a&tags=b → ["a", "b"]
):
    ...
```

| Python 类型 | URL 示例 | 转换结果 |
|------------|---------|---------|
| `int` | `?x=42` | `42` |
| `float` | `?x=9.99` | `9.99` |
| `bool` | `?x=true` | `True` |
| `list[str]` | `?x=a&x=b` | `["a", "b"]` |
| `datetime` | `?x=2026-07-29` | `datetime(2026, 7, 29)` |
| `Enum` | `?x=admin` | `Role.admin` |

---

## 4. 对比表

| 来源 | 写法 | 匹配规则 | 需要额外安装 |
|------|------|---------|------------|
| 路径 | `id: str` | 参数名 = `{name}` | — |
| 查询 | `q: str = ""` | 参数名 = query key | — |
| JSON Body | `body: Model` | 模型字段名 = JSON key | — |
| Form | `x: str = Form()` | 参数名 = form 字段名 | `python-multipart` |
| 文件 | `f: UploadFile` | 参数名 = form 字段名 | `python-multipart` |
| Cookie | `x: str = Cookie()` | 参数名 = cookie 名 | — |
| Header | `x: str = Header()` | 下划线 ↔ 连字符自动转换 | — |
| Request 对象 | `request: Request` | 不匹配，直接拿整个对象 | — |

---

## 5. 分层原则

`Body()`、`Form()`、`Query()`、`Cookie()`、`Header()` 是 HTTP 传输层概念，**只能在 Router 层出现**，不传入 Service 层。

```
Router 层                      Service 层
─────────────────────          ─────────────
Form() 解析 form-data
Body() 解析 JSON          →    转成 dict/Pydantic
Query() 解析 ?key=value        只处理 Python 对象
Cookie() 解析 cookie
```
