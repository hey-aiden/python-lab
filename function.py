# python 函数

"""
函数规则：
1. 函数代码块以 def 关键词开头，后接函数标识符名称和圆括号 ()；
2. 任何传入参数和自变量必须放在圆括号中间，圆括号之间可以用于定义参数;
3. 函数的第一行语句可以选择性地使用文档字符串—用于存放函数说明;
4. 函数内容以冒号起始，并且缩进;
5. return [表达式] 结束函数，选择性地返回一个值给调用方。不带表达式的return相当于返回 None。

def 函数名（参数列表）:
    函数体
"""


def printInfo(name, age):
    "打印任何传入的字符串"
    print("名字: ", name)
    print("年龄: ", age)
    return


printInfo("root", 50)


# 默认参数与可变参数
def countSum(a, b=10):
    print("a = ", a, "b = ", b)
    return a + b


print(countSum(10))
print(countSum(10, 20))


# 可变参数
# *args 会将调用时传入的所有位置参数收集成一个 tuple（元组）
# 例如 countSum(1, 2, 3) 中，args = (1, 2, 3)，类型是 tuple
# 因为 tuple 是可迭代对象，内置函数 sum() 可以直接对其求和
# sum() 接收任意可迭代对象（list/tuple/set 均可），逐个累加其中的数字, python内置函数：sum() 方法对序列进行求和计算
def countSum(*args):
    print("可变参数 args =", args, "| 类型:", type(args))  # <class 'tuple'>
    return sum(args)  # sum() 遍历 tuple，累加所有元素


print("--------------------------------")
print("countSum(1, 2, 3, 4, 5) = ", countSum(1, 2, 3, 4, 5))


# 关键字参数
# **kwargs 会将调用时传入的所有 key=value 参数收集成一个 dict（字典）
# 例如 countSum(a=1, b=2, c=3) 中，kwargs = {'a': 1, 'b': 2, 'c': 3}
# kwargs.values() 返回字典所有的值 [1, 2, 3]，sum() 对其求和
# 优势：调用时参数顺序可以任意，Python 用参数名来匹配，不依赖位置
def countSum(**kwargs):
    print("kwargs =", kwargs, "| 类型:", type(kwargs))  # <class 'dict'>
    print("kwargs.keys():", list(kwargs.keys()))        # 所有参数名
    print("kwargs.values():", list(kwargs.values()))    # 所有参数值
    return sum(kwargs.values())  # 对所有值求和


print(countSum(a=1, b=2, c=3))
