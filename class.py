"""
python 类

class ClassName:
   '类的帮助信息'   #类文档字符串
   class_suite  #类体, 由类成员，方法，数据属性组成

"""


class Person:
    # __init__()方法是一种特殊的方法，被称为类的构造函数或初始化方法，当创建了这个类的实例时就会调用该方法, 类似js对象中的constructor方法
    # self 代表类的实例，self 在定义类的方法时是必须有的，虽然在调用时不必传入相应的参数
    # 类的方法与普通的函数只有一个特别的区别——它们必须有一个额外的第一个参数名称, 按照惯例它的名称是 self
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def say_hello(self):
        print(f"Hello, my name is {self.name} and I am {self.age} years old")

    def hi(self):
        print("hi")


person = Person("John", 30)
person.say_hello()


print("实例属性: ", person.name, person.age)

person.name = "Jane"
person.age = 25
print("修改实例属性后: ", person.name, person.age)


"""
Python 使用了引用计数这一简单技术来跟踪和回收垃圾

在 Python 内部记录着所有使用中的对象各有多少引用。
一个内部跟踪变量，称为一个引用计数器。

当对象被创建时， 就创建了一个引用计数， 当这个对象不再需要时， 也就是说， 这个对象的引用计数变为0 时， 它被垃圾回收。
但是回收不是"立即"的， 由解释器在适当的时机，将垃圾对象占用的内存空间回收。

垃圾回收机制不仅针对引用计数为0的对象，同样也可以处理循环引用的情况。
循环引用指的是，两个对象相互引用，但是没有其他变量引用他们。
这种情况下，仅使用引用计数是不够的。
Python 的垃圾收集器实际上是一个引用计数器和一个循环垃圾收集器。
作为引用计数的补充， 垃圾收集器也会留心被分配的总量很大（即未通过引用计数销毁的那些）的对象。 在
这种情况下， 解释器会暂停下来， 试图清理所有未引用的循环

"""

"""
类的继承

class DerivedClassName(BaseClassName):
    '衍生的类'
    class_suite

BaseClassName（示例中的基类） 必须与派生类定义在一个作用域内。
除了类， 还可以用表达式， 这意味着， 可能要在不同的模块文件中定义一个类， 然后从另一个模块文件中继承它。


"""


class User(Person):
    def __init__(self, name, age, email):
        super().__init__(name, age)
        self.email = email

    # 重写父类方法
    def say_hello(self):
        print(
            f"Hello, my name is {self.name} and I am {self.age} years old and my email is {self.email}"
        )


user = User("John", 30, "john@example.com")
user.say_hello()
user.hi()
