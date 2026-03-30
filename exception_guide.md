# Python 常用异常捕获场景指南

## 1. 文件 / IO 操作

```python
try:
    with open("data.txt", "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    print("文件不存在")
except PermissionError:
    print("没有读取权限")
except UnicodeDecodeError:
    print("文件编码不匹配，尝试指定正确编码")
except OSError as e:
    print(f"系统级IO错误: {e}")
```

## 2. 数据类型转换 / 用户输入

```python
try:
    age = int(input("请输入年龄: "))
    ratio = float("abc")
except ValueError:
    print("输入值不合法")
except TypeError:
    print("类型不匹配，无法转换")
```

## 3. 字典 / 列表访问

```python
data = {"name": "Alice"}
items = [1, 2, 3]

try:
    val = data["age"]    # KeyError
    item = items[10]     # IndexError
except KeyError as e:
    print(f"键不存在: {e}")
except IndexError as e:
    print(f"下标越界: {e}")
# 或统一用基类
except LookupError as e:
    print(f"查找失败: {e}")
```

## 4. 网络请求（requests / httpx 等）

```python
try:
    # requests.get(...) 底层会抛出这些
    pass
except ConnectionRefusedError:
    print("连接被拒绝，服务未启动")
except ConnectionResetError:
    print("连接被重置")
except TimeoutError:
    print("请求超时")
except ConnectionError as e:
    print(f"网络连接错误: {e}")
except OSError as e:
    print(f"底层网络错误: {e}")
```

## 5. 模块导入 / 插件加载

```python
try:
    import numpy as np
except ModuleNotFoundError:
    print("模块未安装，请执行 pip install numpy")
except ImportError as e:
    print(f"导入失败（可能是版本不兼容）: {e}")
```

## 6. 属性 / 变量访问

```python
try:
    obj = None
    obj.name           # AttributeError
    print(undefined)   # NameError
except AttributeError as e:
    print(f"属性不存在: {e}")
except NameError as e:
    print(f"变量未定义: {e}")
```

## 7. 数学运算

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("除数不能为零")
except OverflowError:
    print("数值超出范围")
except ArithmeticError as e:
    print(f"数学运算错误: {e}")
```

## 8. 递归 / 深度调用

```python
def recursive(n):
    return recursive(n + 1)

try:
    recursive(0)
except RecursionError:
    print("递归深度超限，检查终止条件")
```

## 9. 抽象类 / 接口未实现

```python
from abc import ABC, abstractmethod

class Base(ABC):
    @abstractmethod
    def run(self): ...

class Child(Base):
    pass  # 未实现 run

try:
    Child()
except TypeError:
    print("抽象方法未实现，无法实例化")
```

## 10. 程序退出 / 中断处理

```python
import sys

try:
    while True:
        pass
except KeyboardInterrupt:
    print("用户中断，正在清理...")
    sys.exit(0)
except SystemExit as e:
    print(f"程序退出，退出码: {e.code}")
```

## 11. Unicode / 编码处理

```python
try:
    b"\xff\xfe".decode("utf-8")
except UnicodeDecodeError as e:
    print(f"解码失败: {e}")
except UnicodeEncodeError as e:
    print(f"编码失败: {e}")
except UnicodeError as e:
    print(f"Unicode错误: {e}")
```

## 12. 通用兜底（生产环境日志）

```python
import logging

try:
    risky_operation()
except Exception as e:
    logging.exception("未预期的错误")
    raise  # 重新抛出，不吞掉异常
```

---

## 原则总结

| 原则 | 说明 |
|------|------|
| 优先捕获具体异常 | `Exception` 只做兜底，不要一上来就用宽泛的基类 |
| 不要裸 `except:` | 会吞掉 `KeyboardInterrupt` / `SystemExit` |
| 资源释放优先用 `with` | `finally` 作为补充，`with` 更简洁安全 |
| 捕获后要处理或重抛 | 不要静默忽略异常，至少记录日志后 `raise` |
| 利用继承关系简化捕获 | 如用 `OSError` 统一捕获文件相关错误 |
