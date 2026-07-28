# 基本数据类型使用
#
# 规则速查：
# - 函数名: snake_case（全小写 + 下划线）
# - 类名:   PascalCase（首字母大写驼峰）
# - 缩进:   4 个空格（不要用 Tab）


def use_basic_data():
    """演示 Python 基本数据类型的定义和使用。

    规则：
    - 函数第一行写三引号文档字符串（docstring）
    - 参数和返回值用 4 空格缩进
    - 变量名也是 snake_case
    """
    pi = 3.14
    pi = pi + 2
    print(pi)

    isFalse = False
    isTrue = True
    print(isFalse, isFalse + 1)
    print(isTrue, isTrue + 1, isTrue is 1, isTrue == 1)

    strSchool = "ncu"
    print(strSchool)
    strGlue = (
        f"hello {strSchool}"  # f-string（formatted string literal，格式化字符串字面量）
    )
    print(strGlue)

    isNone = None
    print(isNone)


def type_convert():
    """演示 Python 类型转换。

    规则：
    - 函数第一行写三引号文档字符串（docstring）
    - 参数和返回值用 4 空格缩进
    - 变量名也是 snake_case
    """
    print("type_convert")
    pi = 3.14
    print(pi)

    print("数字转boolean:", bool(pi))
    print("数字转字符串:", str(pi))
    print("类型:", type(pi))
