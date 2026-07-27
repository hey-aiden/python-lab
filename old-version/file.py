"""
文件操作：

文件读取如果涉及取数或者某一行的读取，要考虑文件指针的位置，以及文件指针的移动。

tips:
1. file.read() 会把文件指针移到末尾,此时读取 file.readline() 会读取到空字符串；
2. file.readline() 会读取下一行，并且把文件指针移到下一行；
3. file.tell() 会返回文件指针的当前位置；
4. file.seek(offset, from_what) 会移动文件指针到指定位置；

"""

try:
    with open("1.txt.bak", "r") as file:
        fileContent = file.read()
        print(fileContent, "next: ", file.readline())
except Exception as e:
    print(e)


# 读取下一行
try:
    with open("1.txt.bak", "r") as file:
        fileContent = file.readline()
        fileContent2 = file.readline()
        print("readline: ", fileContent)
        print("readline2: ", fileContent2)
except Exception as e:
    print("readline e: ", e)

# 逐行读取下一行
try:
    with open("1.txt.bak", "r") as file:
        for line in file:
            print("for line: ", line)
except Exception as e:
    print("for line error: ", e)
