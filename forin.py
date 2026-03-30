# Python 推导式: 推导式是一种简洁的创建序列的方式，可以用来创建列表、集合和字典;
# 可以从一个数据序列构建另一个新的数据序列的结构体

"""
1. 列表推导式：

[表达式 for 变量 in 列表]
[out_exp_res for out_exp in input_list]

[表达式 for 变量 in 列表 if 条件]
[out_exp_res for out_exp in input_list if condition]

out_exp_res：列表生成元素表达式，可以是有返回值的函数,接受变量并计算值
out_exp：元素变量，是取自于Iterable的项
input_list：是可迭代对象，可以是一个列表，也可以是一个迭代器，也可以是一个生成器
条件：条件语句，可以省略
"""

numsList = [1, 2, 3, 4, 5]
squares = [x**2 for x in numsList]
print(squares)

squares = [x for x in numsList if x > 3]
print(squares)

squares = [x**2 for x in numsList if x % 2 != 0]
print(squares)


"""
2. 字典推导式

{ key_expr: value_expr for value in collection }

或

{ key_expr: value_expr for value in collection if condition }

key_expr：键表达式，用于生成字典的键
value_expr：值表达式，用于生成字典的值
collection：可迭代对象，可以是列表、元组、集合、字典、字符串等
condition：条件表达式，用于过滤可迭代对象中的元素
"""
dictDemo = {x: x + 1 for x in numsList}
print(dictDemo)

"""
3. 集合推导式

{ expression for item in Sequence }
或
{ expression for item in Sequence if conditional }

expression：表达式，用于生成集合的元素
item：元素变量，是取自于Iterable的项
Sequence：可迭代对象，可以是列表、元组、集合、字符串等
conditional：条件表达式，用于过滤可迭代对象中的元素
"""
setDemo = {x + 1 for x in numsList}
print(setDemo)


"""
4. 元组推导式
元组推导式和列表推导式的用法也完全相同，只是元组推导式是用 () 圆括号将各部分括起来，而列表推导式用的是中括号 []，另外元组推导式返回的结果是一个生成器对象

(expression for item in Sequence )
或
(expression for item in Sequence if conditional )

expression：表达式，用于生成元组的元素
item：元素变量，是取自于Iterable的项
Sequence：可迭代对象，可以是列表、元组、集合、字符串等
conditional：条件表达式，用于过滤可迭代对象中的元素
"""
tupleDemo = (x + 1 for x in numsList)
print(tupleDemo, tuple(tupleDemo))
