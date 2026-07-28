# from base_use.basic_data import type_convert, use_basic_data
# from base_use.reference_data import use_reference_data
# from base_use.loop_iter import use_skill_high_level
from base_use.with_handle import use_with


def main():
    """应用入口。

    规则：
    - 模块级导入放文件顶部
    - 顶层的函数/类之间用两个空行分隔
    - __name__ guard 和最后一个函数之间用一个空行
    """
    base_use()


def base_use():
    # use_basic_data()
    # type_convert()
    # use_reference_data()
    # use_skill_high_level()
    use_with()


if __name__ == "__main__":
    main()
