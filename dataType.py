# Python 数据类型完整指南
# 本文件演示 Python 六大标准数据类型及其常用 API

"""
Python 六个标准数据类型：
  不可变类型：Number(数字)、String(字符串)、Tuple(元组)
  可变类型：List(列表)、Dictionary(字典)、Set(集合)
"""

# ── 变量与类型检查 ────────────────────────────────────
# Python 变量无需声明类型，赋值即创建
counter = 100  # int
miles = 1000.0  # float
name = "runoob"  # str

print("counter 类型:", type(counter))  # <class 'int'>
print("miles 类型:", type(miles))  # <class 'float'>
print("name 类型:", type(name))  # <class 'str'>

# 多变量赋值
a = b = c = 1
x, y, z = 10, 20, "hello"
print("a b c:", a, b, c)  # 1 1 1
print("x y z:", x, y, z)  # 10 20 hello


# ══════════════════════════════════════════════════════
# 1. Number（数字）
# ══════════════════════════════════════════════════════
num_int = 42
num_float = 3.14
num_complex = 2 + 3j

# 常用运算
print("abs(-10):", abs(-10))  # 绝对值: 10
print("pow(2,3):", pow(2, 3))  # 幂运算: 8
print("round(3.7):", round(3.7))  # 四舍五入: 4
print("max(1,5,3):", max(1, 5, 3))  # 最大值: 5
print("min(1,5,3):", min(1, 5, 3))  # 最小值: 1

# 类型转换
print("int(3.9):", int(3.9))  # 转整数: 3
print("float(5):", float(5))  # 转浮点: 5.0
print("str(100):", str(100))  # 转字符串: "100"


# ══════════════════════════════════════════════════════
# 2. String（字符串）— 不可变
# ══════════════════════════════════════════════════════
text = "Hello Python"

# 索引与切片
print("text[0]:", text[0])  # 'H'
print("text[-1]:", text[-1])  # 'n'
print("text[0:5]:", text[0:5])  # 'Hello'
print("text[::2]:", text[::2])  # 'HloPto' (步长2)

# 常用方法
print("lower:", text.lower())  # 转小写: 'hello python'
print("upper:", text.upper())  # 转大写: 'HELLO PYTHON'
print("replace:", text.replace("Python", "World"))  # 替换: 'Hello World'
print("split:", text.split())  # 分割: ['Hello', 'Python']
print("startswith:", text.startswith("Hello"))  # True
print("endswith:", text.endswith("Python"))  # True
print("find:", text.find("Python"))  # 查找位置: 6
print("count:", text.count("l"))  # 统计字符: 2
print("strip:", "  space  ".strip())  # 去空格: 'space'
print("join:", "-".join(["a", "b", "c"]))  # 连接: 'a-b-c'


"""
══════════════════════════════════════════════════════
3. List（列表）— 可变，有序
内置函数：
len(list): 计算列表元素个数
max(list): 返回列表中最大的元素
min(list): 返回列表中最小的元素
list(seq): 将元组转换为列表

list.append(obj): 在列表末尾添加新的对象
list.count(obj): 统计某个元素在列表中出现的次数
list.extend(seq): 在列表末尾一次性添加另一个序列中的多个值（用新列表扩展原来的列表）
list.index(obj): 从列表中找出某个值第一个匹配项的索引位置
list.insert(index, obj): 将对象插入列表
list.pop([index=-1]): 移除列表中的一个元素（默认最后一个元素），并且返回该元素的值
list.remove(obj): 移除列表中某个值的第一个匹配项
list.reverse(): 反向列表中元素
list.sort(key=None, reverse=False): 对原列表进行排序
list.clear(): 清空列表
list.copy(): 复制列表
copy.deepcopy(obj): 深复制列表
══════════════════════════════════════════════════════
"""
fruits = ["apple", "banana", "cherry"]

# 访问元素
print("fruits[0]:", fruits[0])  # 'apple'
print("fruits[-1]:", fruits[-1])  # 'cherry'
print("fruits[0:2]:", fruits[0:2])  # ['apple', 'banana']

# 修改元素
fruits[1] = "blueberry"
print("修改后 fruits:", fruits)  # ['apple', 'blueberry', 'cherry']

# 常用方法
fruits.append("orange")  # 末尾添加
fruits.insert(1, "grape")  # 指定位置插入
fruits.extend(["kiwi", "mango"])  # 批量添加
print("append/insert/extend 后:", fruits)

removed = fruits.pop()  # 删除并返回最后一个
fruits.remove("grape")  # 删除指定元素
print("pop 删除:", removed)
print("count('apple'):", fruits.count("apple"))  # 统计元素: 1
print("index('cherry'):", fruits.index("cherry"))  # 查找索引

fruits.sort()  # 排序（原地修改）
fruits.reverse()  # 反转
print("sort+reverse 后:", fruits)
print("len(fruits):", len(fruits))
print("'apple' in fruits:", "apple" in fruits)  # 成员检测

# 列表推导式
squares = [x**2 for x in range(5)]
print("列表推导式 squares:", squares)  # [0, 1, 4, 9, 16]


"""
 ══════════════════════════════════════════════════════
 4. Tuple（元组）— 不可变，有序
 内置函数:
 len(tuple): 计算元组元素个数
 max(tuple): 返回元组中最大的元素
 min(tuple): 返回元组中最小的元素
 tuple(iterable): 将可迭代系列转换为元组
 ══════════════════════════════════════════════════════
 """

tup = ("physics", "chemistry", 1997, 2000)

# 访问与切片
print("tup[0]:", tup[0])  # 'physics'
print("tup[1:3]:", tup[1:3])  # ('chemistry', 1997)
print("tup*2:", tup * 2)  # 重复元组
print("tup+('test',):", tup + ("test",))  # 连接元组

# 常用方法（元组方法很少，因为不可变）
print("count(1997):", tup.count(1997))  # 统计元素: 1
print("index('chemistry'):", tup.index("chemistry"))  # 查找索引: 1
print("len(tup):", len(tup))  # 长度: 4
print("将可迭代列表[1,2,3,4]转换为元组：", tuple([1, 2, 3, 4]))

# 元组解包
a, b, c, d = tup
print("元组解包 a b:", a, b)  # physics chemistry

# 生成器表达式（注意：() 不是元组推导式，而是生成器）
gen = (x**2 for x in range(5))
print("生成器转列表:", list(gen))  # [0, 1, 4, 9, 16]


# ══════════════════════════════════════════════════════
# 5. Set（集合）— 可变，无序，不重复
# ══════════════════════════════════════════════════════
sites = {"Google", "Taobao", "Runoob", "Taobao"}  # 自动去重
print("集合(自动去重):", sites)

# 成员检测
print("'Google' in sites:", "Google" in sites)  # True

# 常用方法
sites.add("YouTube")
sites.update(["Facebook", "Twitter"])
print("add/update 后:", sites)
sites.remove("Taobao")  # 删除（不存在会报错）
sites.discard("NotExist")  # 删除（不存在不报错）
popped = sites.pop()
print("pop 删除:", popped)
print("len(sites):", len(sites))

# 集合运算
set1 = {1, 2, 3, 4}
set2 = {3, 4, 5, 6}
print("并集 set1|set2:", set1 | set2)  # {1, 2, 3, 4, 5, 6}
print("交集 set1&set2:", set1 & set2)  # {3, 4}
print("差集 set1-set2:", set1 - set2)  # {1, 2}
print("对称差 set1^set2:", set1 ^ set2)  # {1, 2, 5, 6}


# ══════════════════════════════════════════════════════
# 6. Dictionary（字典）— 可变，Python 3.7+ 保持插入顺序
# ══════════════════════════════════════════════════════
person = {"name": "Alice", "age": 25, "city": "Beijing"}

# 访问元素
print("person['name']:", person["name"])  # 'Alice'
print("get('age'):", person.get("age"))  # 25
print("get('job',默认):", person.get("job", "未知"))  # 键不存在返回默认值

# 修改与添加
person["age"] = 26
person["job"] = "Engineer"

# 常用方法
print("keys:", person.keys())
print("values:", person.values())
print("items:", person.items())

person.update({"salary": 10000})
removed = person.pop("city")
print("pop('city'):", removed)
print("len(person):", len(person))

# 遍历字典
print("遍历字典:")
for key, value in person.items():
    print(f"  {key}: {value}")

# 字典推导式
squared = {x: x**2 for x in range(5)}
print("字典推导式:", squared)  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}


# ══════════════════════════════════════════════════════
# 类型转换总结
# ══════════════════════════════════════════════════════
print("str→list:", list("abc"))  # ['a', 'b', 'c']
print("list→tuple:", tuple([1, 2, 3]))  # (1, 2, 3)
print("list→set(去重):", set([1, 2, 2, 3]))  # {1, 2, 3}
print("list→dict:", dict([("a", 1), ("b", 2)]))  # {'a': 1, 'b': 2}
