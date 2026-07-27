"""
模块使用:
1. 导入模块
2. 使用模块中的函数
"""

# 全局导入：导入模块中的所有函数
# import utils
# utils.print_info("root", 50)

# 局部导入：导入模块中的指定函数
# from utils import print_info
# print_info("root", 50)

# 别名导入：导入模块中的指定函数，并给函数起一个别名
from utils import print_info as print_info_alias

print_info_alias("root", 51)
