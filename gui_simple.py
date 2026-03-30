# 最简版 GUI 测试
import tkinter as tk

print("正在创建窗口...")
root = tk.Tk()
print("窗口创建成功")

root.title("测试")
root.geometry("300x200")

label = tk.Label(root, text="如果能看到这个就说明 tkinter 没问题！")
label.pack()

print("进入主循环...")
root.mainloop()
print("程序退出")
