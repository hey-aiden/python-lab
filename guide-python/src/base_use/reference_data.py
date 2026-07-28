# 引用类型
#
# 规则速查：
# - 函数名: snake_case
# - 类名:   PascalCase
# - ⚠️ 不要用 list/dict/set/tuple 做变量名，会遮蔽 Python 内置函数


def use_reference_data():
    """演示 Python 引用类型。"""
    # use_list()
    # use_tuple()
    # use_dict()
    # use_set()
    # use_frozenset()


# 列表: 可变有序序列
def use_list():
    print("use list:")
    items = [1, 2, 3, 4, 5]  # ⚠️ 不要用 list 做变量名
    items.append(6)
    print(items)  # [1, 2, 3, 4, 5, 6]
    print(items[-1])  # 6 — 负数索引从尾部取


# 元组: 不可变有序序列
def use_tuple():
    print("use tuple:")
    coords = (1, 2, 3, 4, 5)  # ⚠️ 不要用 tuple 做变量名
    print(coords)  # (1, 2, 3, 4, 5)
    print(coords[-1])  # 5


# 字典: 键值对
def use_dict():
    print("use dict:")
    user = {"name": "John", "age": 30}  # ⚠️ 不要用 dict 做变量名
    print(user, user.keys(), user.values())
    print(user["name"], user.get("school", "ncu"))  # get 安全取值
    for key, value in user.items():
        print(key, value)


# 集合: 无序不重复元素集
def use_set():
    print("use set:")
    tags = {1, 2, 3, 4, 5}  # ⚠️ 不要用 set 做变量名
    print(tags)  # {1, 2, 3, 4, 5}（顺序不保证）
    # set 不支持索引！用 in 判断成员：
    print(3 in tags)  # True — O(1) 成员判断
    tags.add(6)
    print(tags)  # {1, 2, 3, 4, 5, 6}
    tags.remove(6)
    print(tags)  # {1, 2, 3, 4, 5}
    tags.clear()
    print(tags)  # set()


# 不可变集合: frozenset
def use_frozenset():
    print("use frozenset:")
    # ⚠️ 变量名不要叫 frozenset，会遮蔽内置函数！
    # frozenset = frozenset(...) ← 右边 frozenset 被当成本地变量，UnboundLocalError
    frozen = frozenset({1, 2, 3, 4, 5})
    print(frozen)  # frozenset({1, 2, 3, 4, 5})
    # frozen.add(6)            # ❌ 不可变，无法修改
