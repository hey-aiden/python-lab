# 作用域与引用安全

> 📖 本章讲解变量的作用域规则（LEGB）与引用类型的安全使用，是第 7 章「变量与可变性」的进阶篇。建议在第 7 章之后阅读。

### 10.1 作用域查找 — LEGB 规则

```python
# Python 查找一个名字时，按 LEGB 顺序从内向外找：
#   Local     — 当前函数内部
#   Enclosing — 外层函数（闭包场景）
#   Global    — 模块（文件）顶层
#   Built-in  — 内置（len、print、range...）

x = "global"            # G：模块级

def outer():
    x = "enclosing"     # E：外层函数的局部
    def inner():
        x = "local"     # L：inner 自己的局部
        print(x)        # "local" — 就近原则
    inner()

outer()
```

### 10.2 没有块级作用域 — 与 JS 最大的差异

```python
# JS：let/const 是块级作用域
#   { let x = 1; }  console.log(x)  // ReferenceError

# Python：if / for / while / try / with 都不产生新作用域
if True:
    x = 1
print(x)                # 1 — x 泄漏到模块作用域

for i in range(3):
    pass
print(i)                # 2 — 循环变量也泄漏（不像 JS 的 let）

# 例外：推导式在 Python 3 有独立作用域，不泄漏
[x for x in range(3)]
# print(x)              # NameError
```

### 10.3 函数内赋值即声明局部变量

```python
x = 1

def f():
    print(x)    # ❌ UnboundLocalError！
    x = 2       # 函数内只要对 x 赋值，整个函数的 x 都被当成局部变量

# 规则：函数内对某名字赋值（含 += 等），它就覆盖整个函数体成为局部变量。
# 想读全局又要改它，用 global（见 10.4）
```

### 10.4 global 与 nonlocal

```python
count = 0

def inc():
    global count        # 声明要修改模块级变量
    count += 1

# nonlocal — 修改外层（闭包）变量，而不是全局，只能在嵌套函数和闭包函数内部定义，因为它的作用就是指“不是当前函数的本地，但在某个外层函数里”，
# 所以不能直接在最外层函数中使用。
def make_counter():
    count = 0
    def inc():
        nonlocal count  # 改 make_counter 里的 count，而非新建局部变量
        count += 1
        return count
    return inc

c = make_counter()
c()   # 1
c()   # 2
```

### 10.5 闭包 — 函数记住外层变量

```python
def multiply_by(n):
    def inner(x):
        return x * n    # inner 捕获了 n
    return inner

double = multiply_by(2)
double(5)   # 10

# ⚠️ 循环里的闭包 — 晚绑定（late binding）陷阱，类似 JS 的 var 循环
funcs = []
for i in range(3):
    funcs.append(lambda: i)      # 所有 lambda 记住的都是同一个 i
print([f() for f in funcs])      # [2, 2, 2] — 不是 [0, 1, 2]

# ✅ 用默认参数把值"固定"在定义时
funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])      # [0, 1, 2]
```

### 10.6 引用：别名与共享

```python
a = [1, 2, 3]
b = a            # b 是 a 的别名，指向同一个列表对象
b.append(4)
print(a)         # [1, 2, 3, 4] — a 也变了

# 判断是否同一对象
a is b           # True
id(a) == id(b)   # True — id() 返回对象的内存标识
```

### 10.7 函数传参：赋值传递（传引用）

```python
# Python 既不是"传值"也不是"传引用"，而是"传引用 + 绑定"
def f(lst):
    lst.append(4)   # 修改可变对象 → 影响调用者
    lst = [9]       # 重新绑定 → 只改局部名字，不影响调用者

a = [1, 2, 3]
f(a)
print(a)            # [1, 2, 3, 4]（append 生效，lst = [9] 没生效）

# 记忆：参数是"名字的别名"。改对象内容会传导，重新赋值不会。
```

### 10.8 可变默认参数 — 经典坑（主 README 坑 7）

```python
def f(lst=[]):      # ❌ 默认值在函数定义时求值一次，所有调用共享同一个列表
    lst.append(1)
    return lst

f()   # [1]
f()   # [1, 1]      ← 第二次调用累积了上次的结果！

# ✅ 正确写法：用 None 占位，调用时再新建
def f(lst=None):
    if lst is None:
        lst = []
    lst.append(1)
    return lst
```

### 10.9 浅拷贝 vs 深拷贝

```python
import copy

a = [[1, 2], [3, 4]]

b = a.copy()            # 浅拷贝：外层是新列表，内层列表仍共享
b[0].append(99)
print(a)                # [[1, 2, 99], [3, 4]] — a 的内层也被改了！

c = copy.deepcopy(a)    # 深拷贝：内外层全部独立
c[0].append(100)
print(a)                # [[1, 2, 99], [3, 4]] — a 不受影响
```

### 10.10 防御性拷贝 — 保护内部状态

```python
class Config:
    def __init__(self, items):
        self.items = list(items)   # 拷贝一份，外部改原列表不影响内部状态
        # 注意：list(items) 是浅拷贝，若 items 里有嵌套可变对象，需 copy.deepcopy

# 同理，返回内部可变对象时也应返回副本，避免外部意外改动
```

### 10.11 其他引用陷阱

```python
# 1) 乘法创建的嵌套列表 — 共享内层
grid = [[0]*3]*3       # ❌ 三个元素是同一个内层列表的引用
grid[0][0] = 1
print(grid)            # [[1,0,0],[1,0,0],[1,0,0]] — 全变了

grid = [[0]*3 for _ in range(3)]   # ✅ 每次推导式新建独立内层列表

# 2) += 原地修改 vs + 新建
a = [1, 2]; b = a
a = a + [3]     # 新建列表，a 重新绑定，b 仍是 [1, 2]
print(b)        # [1, 2]

a = [1, 2]; b = a
a += [3]        # 原地扩展（等价 a.extend([3])），b 也跟着变
print(b)        # [1, 2, 3]

# 3) 遍历时修改列表 — 会跳过元素
a = [1, 2, 3]
for x in a[:]:      # ✅ 遍历副本
    a.remove(x)

# 4) 可变对象不能做字典 key
d = {[1, 2]: "x"}   # TypeError: unhashable type: 'list'
```

### 10.12 跨模块导入变量 — 引用共享的边界

```python
# config.py
counter = 0            # 不可变类型
data = [1, 2, 3]       # 可变类型

# worker.py
from config import counter, data

counter += 1           # ❌ 只是重新绑定了 worker 里的 counter，config.counter 仍是 0
data.append(4)         # ✅ 原地修改共享对象，config.data 变成 [1, 2, 3, 4]
```

`from config import x` 拿到的是「`config.x` 当时指向的对象」的**引用快照**，不是到 `config.x` 的实时连接。所以：

- **可变类型**（list/dict/实例）：改内容 → 所有模块共享同一个对象，改动会传导；
- **不可变类型**（str/int/tuple）：无法原地改，「改」= 重新绑定 → 只影响本模块，其他模块仍保留**初始值**。

```python
# ─── 想要跨模块实时读写状态 ───

# 方案一：import module，访问 module.xxx（实时取属性）
import config
config.counter += 1        # ✅ 给模块对象设属性，所有 import config 的地方都看到

# 方案二：把状态包装成引用类型对象（类实例的字段 / 字典）
# config.py
class AppState:
    def __init__(self):
        self.counter = 0

state = AppState()         # 单例

# 任意模块
from config import state
state.counter += 1         # ✅ 修改共享对象的字段，全局生效
```

> ⚠️ 需要跨模块共享可变状态时，优先「可变对象 + 原地修改」，而不是 `from ... import` 后重新赋值。

---

### 本节要点

- **LEGB**：名字按 Local → Enclosing → Global → Built-in 从内向外查找。
- **没有块级作用域**：`if`/`for`/`while` 不产生新作用域，循环变量会泄漏；推导式例外。
- **函数内赋值 = 声明局部变量**，会覆盖整个函数体；读全局用 `global`，改闭包用 `nonlocal`。
- **赋值即绑定**：多个名字可指向同一可变对象，通过别名修改会相互影响。
- **传参是「赋值传递」**：改对象内容会传导给调用者，重新赋值不会。
- **可变默认参数**是共享陷阱，用 `None` 占位。
- **浅拷贝**只复制外层，**深拷贝**（`copy.deepcopy`）才彻底独立。
- 需要对外隔离可变状态时，用**防御性拷贝**。
- **`from module import x` 是引用快照**：可变对象改内容才共享；跨模块共享不可变状态要包装成可变对象（字段/字典），或用 `import module` 实时访问。

---

[← 上一章：错误捕获](09-errors.md) | [下一章：模块导入与标准库 →](11-standard-library.md)
