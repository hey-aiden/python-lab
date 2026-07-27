# python流程控制与循环语句

var1 = 100

# if...else语句
if var1:
    print("1 - if 表达式条件为 true")
    print(var1)
else:
    print("1 - if 表达式条件为 false")
    print(var1)

if var1:
    print("2 - if 表达式条件为 true")
    print(var1)
else:
    print("2 - if 表达式条件为 false")
    print(var1)

# match...case语句
x = 1
match x:
    case 1:
        print("x is 1")
    case 2:
        print("x is 2")
    case _:  # _ 表示默认值
        print("x is not 1 or 2")


# while...else语句
count = 0
while count < 5:
    print(count, " is less than 5")
    count = count + 1
else:
    print(count, " is not less than 5")


# for...else语句  range(5): range() 函数, 生成一个指定的序列, 默认从0开始, 步长为1
# range(5): 0,1,2,3,4
# range(1,5): 1,2,3,4
# range(1,5,2): 1,3
for i in range(5):
    print(i)
else:
    print("else: for loop is over")


# break语句: 跳出 for 和 while 的循环体
# 注意：触发 break 后，else 块不会执行
for i in range(5):
    if i == 3:
        print("break: i == 3，跳出循环")
        break
    print("当前 i:", i)
else:
    print("break: for loop is over")  # break 触发时此行不会执行


# continue语句: 告诉 Python 跳过当前循环块中的剩余语句，然后继续进行下一轮循环
for i in range(5):
    if i == 3:
        continue
    print(i)
else:
    print("continue for loop is over")

# pass语句： pass是空语句，是为了保持程序结构的完整性，一般用作占位语句。
for i in range(5):
    if i == 3:
        pass
    print(i)
else:
    print("pass: for loop is over")
