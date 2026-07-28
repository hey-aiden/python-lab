# 数据类型对照

> 📖 本章是 Python 语言基础的第一站，以 JS 对照方式讲解所有内置类型。

### 6.1 整体映射

| JavaScript | Python | 关键差异 |
|------------|--------|----------|
| `number` | `int` / `float` | JS 统一为 64-bit 浮点；Python 区分整数和浮点 |
| `bigint` | `int` | Python 的 `int` 天生支持任意精度，无需 BigInt |
| `string` | `str` | 都是不可变 Unicode 字符串 |
| `boolean` | `bool` | Python 写作 `True` / `False`（首字母大写），且是 `int` 的子类 |
| `undefined` | ❌ 不存在 | Python 用 `None`，但 `None` 更接近 JS 的 `null` |
| `null` | `None` | 唯一的空值，只有一个实例 |
| `Symbol` | ❌ 不存在 | Python 通常用字符串常量替代 |
| `Array` | `list` | 可变、有序；Python 没有 `.map()`/`.filter()` 方法，用推导式代替 |
| `Object` | `dict` | 键必须是可哈希类型（字符串、数字、元组等），不支持 `.` 点号访问 |
| `Map` | `dict` | Python 的 `dict` 本质就是哈希表，直接用即可 |
| `Set` | `set` | 都表示无序不重复集合 |

### 6.2 各类型详解

#### 数值 — `number` → `int` / `float`

```python
# JS: let n = 42;  let f = 3.14;
n = 42           # int — 不限精度，随便多大
f = 3.14         # float — 64-bit 双精度，和 JS number 相同

1_000_000        # 可以用 _ 分隔数字，纯视觉辅助

# 浮点精度问题 — 和 JS 一模一样
0.1 + 0.2        # 0.30000000000000004
```

#### 布尔 — `boolean` → `bool`

```python
True              # 首字母大写！！
False

# bool 是 int 子类（JS 里可没这种关系）
True + 1          # 2（True 即 1）
True is 1         # False，类型不同但值等价

# 假值判断（和 JS 差别很大，这是最大坑之一）
# Python 中以下为 False：
bool(False)       # False
bool(None)        # False
bool(0)           # False
bool(0.0)         # False
bool("")          # False  — 空字符串
bool([])          # False  — 空列表
bool({})          # False  — 空字典
bool(())          # False  — 空元组
# 其他全是 True（跟 JS 的 truthy/falsy 规则不同）
```

#### 字符串 — `string` → `str`

```python
# 单引号和双引号无区别，和 JS 一样
"hello" == 'hello'   # True

# 模板字符串 = f-string（JS 的 `` 反引号）
name = "world"
f"hello {name}"           # "hello world"
f"1 + 1 = {1 + 1}"        # "1 + 1 = 2"

# 常用操作
"a,b,c".split(",")         # ['a', 'b', 'c']  — 同 JS
",".join(["a", "b"])       # "a,b"  — 注意是 str 的方法，不是 Array 的
" hello ".strip()          # "hello"  — 同 trim()
"hello".upper()            # "HELLO"  — 注意是 upper 不是 toUpperCase
```

#### 列表 — `Array` → `list`

```python
# 创建和访问
items = [1, 2, 3]
items[0]            # 1
items[-1]           # 3  — 负数索引从尾部取，JS 没有
items[1:3]          # [2, 3]  — 切片（slice），比 JS 更强大

# 增删改
items.append(4)     # [1,2,3,4]  — 同 push
items.pop()         # 4，弹出最后一个 — 同 pop
items.insert(0, 0)  # [0,1,2,3]  — 指定位置插入

# ⚠️ JS 开发者最容易犯错：list 的 + 是拼接，不是合并
[1, 2] + [3, 4]     # [1, 2, 3, 4]  — 同 JS 的 .concat()

# ⚠️ 第二个坑：Python 没有 .map() / .filter() 方法！
# JS:  arr.map(x => x * 2)
# Python：用推导式（下一节详讲）
[x * 2 for x in items]                   # [2, 4, 6]
[x for x in items if x > 1]              # [2, 3]
```

#### 元组 — `Tuple`（JS 无对应物）

```python
coords = (10, 20)    # 不可变的列表
coords[0]            # 10
coords[0] = 5        # ❌ TypeError: tuple 不支持修改

# 解包赋值 — 同 JS 解构
x, y = (10, 20)      # x=10, y=20
x, y = y, x          # 一行交换，无需临时变量

# 单元素元组的坑 — 逗号是灵魂，括号只是外壳
t = (1)              # ❌ 这是 int 1，不是 tuple
t = (1,)             # ✅ 这才是元组
```

#### 字典 — `Object` → `dict`

```python
user = {"name": "Alice", "age": 30}

# 访问
user["name"]          # "Alice"
user.get("email", "") # ""  — 安全访问，不存在则返回默认值（推荐）

# ⚠️ 不能点号访问！
user.name             # ❌ AttributeError（除非是类实例属性）

# 增删
user["email"] = "a@b.com"
del user["email"]          # 删除键
user.pop("email", None)    # 安全删除

# 遍历
for key in user:               # 同 Object.keys()
    pass
for key, value in user.items(): # 同 Object.entries()
    pass

# ⚠️ 键类型限制：只能是可哈希类型
#   合法：str, int, float, tuple
#   非法：list, dict, set（这些东西不能做 key）
```

#### 集合 — `Set` → `set`

```python
tags = {"python", "js"}
tags.add("rust")
"rust" in tags       # True  — O(1) 成员判断

# 集合运算
a = {1, 2, 3}
b = {2, 3, 4}
a & b                # {2, 3}    — 交集
a | b                # {1,2,3,4} — 并集
a - b                # {1}       — 差集
```

#### 空值与字节 — `null`/`Buffer` → `None`/`bytes`

```python
# None — 唯一的空值（同时扮演 JS 的 null 和 undefined）
result = None
if result is None:        # 用 is，不要用 ==（约定俗成）
    pass

# 可选链 ?. 的替代写法
obj = {"key": "value"}                    # 示例数据（dict）
value = obj.get("key")                    # dict 的 get — 安全取值
value = obj.get("missing", "默认值")       # 不存在则返回默认值

class Config:                             # 示例数据（对象）
    name = "Alice"
cfg = Config()
value = getattr(cfg, 'name', 'default')   # 对象属性 — 不存在则返回默认值
value = getattr(cfg, 'missing', 'default')  # 'default'

# bytes — 二进制数据，类似 JS 的 Uint8Array 或 Buffer
data = b"hello"
data = "你好".encode("utf-8")    # str → bytes
text = data.decode("utf-8")      # bytes → str
```

