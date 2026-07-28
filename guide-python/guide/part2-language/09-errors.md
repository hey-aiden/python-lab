# 错误捕获

> 📖 本章讲解异常处理、with 语句和常见内置异常。建议在第 6-8 章之后阅读。

### 9.1 语法对照

```python
# JS:
#   try { ... } catch (error) { ... } finally { ... }
#   throw new Error("msg")

# Python:
try:
    result = 1 / 0
except ZeroDivisionError as e:
    # 捕获特定异常
    print(f"出错了: {e}")
except (TypeError, ValueError) as e:
    # 同时捕获多种
    pass
except Exception as e:
    # 捕获所有（类似 JS 的 catch(error)）
    pass
else:
    # try 块无异常时执行（JS 没有这个）
    print("一切正常")
finally:
    # 无论如何都执行
    print("清理")
```

### 9.2 关键差异

```python
# Python 鼓励捕获具体异常类型，而不是一把抓
try:
    data = json.loads(raw)
except json.JSONDecodeError:      # ✅ 精确捕获
    data = {}

# raise — 类似 throw
raise ValueError("无效参数")
raise   # 单独使用 = 重新抛出当前异常（在 except 块内）

# 自定义异常
class MyError(Exception):
    pass

# 常见内置异常
# TypeError      — 类型不对（传了 str 给期望 int 的参数）
# ValueError     — 类型对但值不对（int("abc")）
# KeyError       — 字典 key 不存在（类似访问对象不存在的属性）
# IndexError     — 列表索引越界
# AttributeError — 对象没有该属性
# ImportError    — 模块导入失败
# FileNotFoundError — 文件不存在
```

### 9.3 资源管理 — `with` 替代 try-finally

```python
# JS 没有直接对应的，类似 C# using 或 Java try-with-resources

# 文件读写 — 自动关闭，无需 finally
with open("file.txt", "r") as f:
    content = f.read()
# 这里文件已自动关闭，不需要 f.close()

# 等价于：
f = open("file.txt", "r")
try:
    content = f.read()
finally:
    f.close()   # 手动保证关闭
```

