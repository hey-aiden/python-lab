def use_skill_high_level():
    print("use skill high level:")
    # for_loop()
    # for_exp()
    use_iter()


def for_loop():
    items = [1, 2, 3]
    for item in items:
        if item > 2:
            print("item > 2:", item)
        else:
            print("item <= 2:", item)

    user = {"name": "John", "age": 30}
    for key, value in user.items():
        print(key, value)

    for i in range(10):
        print(i)


# python 推导式
def for_exp():
    items = [1, 2, 3, 4, 5]
    double_items = [item * 2 for item in items]
    print(double_items)

    scoresTuple = (85, 90, 78, 92, 88)
    passed = [score for score in scoresTuple if score >= 80]
    print(passed)


def use_iter():
    items = [1, 2, 3]
    itCtx = iter(items)
    print(next(itCtx))  # 1
    print(next(itCtx))  # 2
    print(next(itCtx))  # 3
    # ⚠️ 再调一次 next() 会 StopIteration，因为迭代器已耗尽
    # 安全写法：next(itCtx, default) — 耗尽时返回默认值
    print(next(itCtx, "empty"))  # "empty"
