# 变量、赋值与可变性

> 📖 本章是 Python 最核心的心智模型：赋值即绑定、可变 vs 不可变、== vs is。建议在第 6 章之后阅读。

### 7.1 变量定义 — 无声明关键字

```python
# JS:  let name = "Alice";   const MAX = 100;
# Python：直接赋值，没有 let/const/var
name = "Alice"
MAX = 100          # 全大写只是约定，没有真正的常量
```

Python **没有常量关键字**。全大写命名（`MAX_SIZE`）是社区约定，告诉别人"别改它"，但语言层面不阻止。

### 7.2 可变性 — 核心概念

```python
# JS 里：const arr = [1,2]; arr.push(3); // 合法，const 只锁引用不锁内容
# Python 同理，但分类更清晰：

# 不可变类型（immutable）：
#   int, float, str, bool, tuple, frozenset, bytes, None
#   创建后内容不可修改，任何"修改"操作都产生新对象

s = "hello"
s = s + " world"    # 看起来像修改，实际创建了新字符串，原 "hello" 未变
id(s)                # 查看对象在内存中的唯一标识（类似 JS 的 === 指针比较）

# 可变类型（mutable）：
#   list, dict, set, bytearray
#   内容可原地修改

a = [1, 2, 3]
b = a               # b 和 a 指向同一列表
b.append(4)
print(a)            # [1, 2, 3, 4]  — a 也变了！

# 想复制一份独立列表？
b = a.copy()        # 浅拷贝
b = a[:]            # 同上，切片拷贝
import copy
b = copy.deepcopy(a) # 深拷贝
```

### 7.3 值与引用（赋值即绑定）

```python
# Python 的赋值 = 给对象贴名字标签，不复制数据

# 不可变类型的行为 — 看起来像"值传递"
x = 1
y = x               # y 和 x 指向同一个 int 对象 1
y = 2               # y 现在指向新的 int 对象 2，x 还是 1

# 可变类型的行为 — 看起来像"引用传递"
a = [1, 2]
b = a               # a 和 b 都指向同一个列表
b[0] = 99
print(a[0])         # 99，两个名字指向同一个东西
```

### 7.4 `==` vs `is`

```python
# ==  比较值是否相等（类似 JS 的 ===，但不做隐式类型转换）
#     "1" == 1 在 Python 中为 False（在 JS 的 == 中为 True）
# is  比较是否同一个对象（类似 JS 的 Object.is 或指针比较）

a = [1, 2]
b = [1, 2]
c = a

a == b              # True  — 值相等
a is b              # False — 不同对象
a is c              # True  — 同一个对象

# 对 None 永远用 is（约定俗成，比 == 更规范）
x = None
if x is None:       # ✅ 正确
if x == None:       # 可以但不符合惯例
```

