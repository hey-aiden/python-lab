# python regex正则模块


import re


pattern = r"hello"

text = "hello world"

# re.match() 函数用于从字符串的起始位置匹配正则表达式。如果匹配成功，返回一个匹配对象；否则返回 None
match = re.match(pattern, text)


print(match, match.group())


# None 在 Python 里是唯一的对象（singleton），所以用 is 判断最准确； 虽然也可以用type语句：isinstance(res, type(None))，但更推荐用 is 判断。
res = re.match(pattern, "123")
print(res is None)  # None
print(isinstance(res, type(None)))  # None
