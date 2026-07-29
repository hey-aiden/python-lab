from base_use.index import exec_entry


def main():
    """应用入口。

    规则：
    - 模块级导入放文件顶部
    - 顶层的函数/类之间用两个空行分隔
    - __name__ guard 和最后一个函数之间用一个空行
    """
    base_use()


def base_use():
    exec_entry()


if __name__ == "__main__":
    main()
