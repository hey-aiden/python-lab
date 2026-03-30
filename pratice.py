"""
多变量赋值/序列解包:
· 左右数量必须一致
· 可以用于“交换变量”
· 可以接收函数返回值
· 可以忽略变量
"""

a, b, c = 1, 2, 3
print(a, b, c)

a, b, c = [1, 2, 3]
print(a, b, c)

a, b, c = (1, 2, 3)
print(a, b, c)

a, b, c = {1, 2, 3}
print(a, b, c)


a, b = b, a
print(a, b)


def init_num():
    return 11, 22, 33


a, _, b = init_num()  # _ 表示忽略该值
print(a, b)
