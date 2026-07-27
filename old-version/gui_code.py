# GUI编程 - 交互式用户界面示例
# 使用 tkinter 实现，Python 内置 GUI 库

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ==================== 主窗口创建 ====================

# 创建主窗口对象
root = tk.Tk()

# 设置窗口标题
root.title("Python GUI 学习")

# 设置窗口大小（宽x高）
root.geometry("500x400")

# 设置窗口最小尺寸
root.minsize(400, 300)

# 设置窗口背景色
root.configure(bg="#f0f0f0")

# ==================== 变量定义 ====================

# StringVar - 用于绑定输入框，可以自动更新和获取值
name_var = tk.StringVar()
email_var = tk.StringVar()
# IntVar - 用于复选框
agree_var = tk.IntVar(value=0)

# ==================== 函数定义 ====================

def on_submit():
    """提交按钮点击事件"""
    name = name_var.get()
    email = email_var.get()
    agreed = agree_var.get()
    
    # 验证输入
    if not name:
        # 显示警告消息框
        messagebox.showwarning("警告", "请输入姓名！")
        return
    
    if not email:
        messagebox.showwarning("警告", "请输入邮箱！")
        return
    
    if not agreed:
        messagebox.showwarning("警告", "请先同意条款！")
        return
    
    # 添加到列表
    tree.insert("", tk.END, values=(name, email))
    
    # 清空输入框
    name_var.set("")
    email_var.set("")
    agree_var.set(0)
    
    # 显示成功消息
    messagebox.showinfo("成功", f"用户 {name} 添加成功！")


def on_clear():
    """清空按钮点击事件"""
    name_var.set("")
    email_var.set("")
    agree_var.set(0)


def on_delete():
    """删除按钮点击事件"""
    # 获取选中的项
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("警告", "请先选择要删除的项！")
        return
    
    # 确认删除
    if messagebox.askyesno("确认", "确定要删除选中项吗？"):
        for item in selected:
            tree.delete(item)


def on_select_file():
    """选择文件按钮点击事件"""
    # 打开文件选择对话框
    file_path = filedialog.askopenfilename(
        title="选择文件",
        filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
    )
    if file_path:
        messagebox.showinfo("已选择", f"文件路径:\n{file_path}")


def on_about():
    """关于菜单点击事件"""
    messagebox.showinfo(
        "关于",
        "Python GUI 学习示例\n\n"
        "使用 tkinter 构建\n"
        "展示了常用 GUI 组件的用法"
    )


# ==================== 菜单栏创建 ====================

# 创建菜单栏
menubar = tk.Menu(root)

# 文件菜单
file_menu = tk.Menu(menubar, tearoff=0)  # tearoff=0 禁止撕下菜单
file_menu.add_command(label="选择文件", command=on_select_file)
file_menu.add_separator()  # 添加分隔线
file_menu.add_command(label="退出", command=root.quit)
menubar.add_cascade(label="文件", menu=file_menu)

# 帮助菜单
help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(label="关于", command=on_about)
menubar.add_cascade(label="帮助", menu=help_menu)

# 设置菜单栏到窗口
root.config(menu=menubar)

# ==================== 主框架 ====================

# 创建主框架容器，用于组织布局
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

# ==================== 输入区域 ====================

# 创建输入区域框架
input_frame = ttk.LabelFrame(main_frame, text="用户信息", padding="10")
input_frame.pack(fill=tk.X, pady=5)

# 姓名输入
# grid 布局：row=行, column=列, sticky=对齐方式
ttk.Label(input_frame, text="姓名:").grid(row=0, column=0, sticky=tk.W, pady=5)
name_entry = ttk.Entry(input_frame, textvariable=name_var, width=30)
name_entry.grid(row=0, column=1, padx=5, pady=5)

# 邮箱输入
ttk.Label(input_frame, text="邮箱:").grid(row=1, column=0, sticky=tk.W, pady=5)
email_entry = ttk.Entry(input_frame, textvariable=email_var, width=30)
email_entry.grid(row=1, column=1, padx=5, pady=5)

# 复选框
agree_check = ttk.Checkbutton(
    input_frame,
    text="我同意用户条款",
    variable=agree_var
)
agree_check.grid(row=2, column=0, columnspan=2, pady=5)

# ==================== 按钮区域 ====================

# 创建按钮区域框架
button_frame = ttk.Frame(main_frame)
button_frame.pack(fill=tk.X, pady=10)

# 提交按钮
submit_btn = ttk.Button(button_frame, text="提交", command=on_submit)
submit_btn.pack(side=tk.LEFT, padx=5)

# 清空按钮
clear_btn = ttk.Button(button_frame, text="清空", command=on_clear)
clear_btn.pack(side=tk.LEFT, padx=5)

# 删除按钮
delete_btn = ttk.Button(button_frame, text="删除选中", command=on_delete)
delete_btn.pack(side=tk.LEFT, padx=5)

# 选择文件按钮
file_btn = ttk.Button(button_frame, text="选择文件", command=on_select_file)
file_btn.pack(side=tk.LEFT, padx=5)

# ==================== 列表展示区域 ====================

# 创建列表区域框架
list_frame = ttk.LabelFrame(main_frame, text="用户列表", padding="10")
list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

# 创建 Treeview 组件（表格视图）
# columns 定义列名，show="headings" 隐藏首列（默认的树形列）
tree = ttk.Treeview(
    list_frame,
    columns=("name", "email"),
    show="headings",
    height=6
)

# 设置列标题
tree.heading("name", text="姓名")
tree.heading("email", text="邮箱")

# 设置列宽
tree.column("name", width=150)
tree.column("email", width=250)

# 添加滚动条
scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

# 布局 Treeview 和滚动条
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# ==================== 状态栏 ====================

# 创建状态栏
status_bar = ttk.Label(
    root,
    text="就绪 - 点击按钮进行操作",
    relief=tk.SUNKEN,  # 凹陷效果
    anchor=tk.W  # 文字左对齐
)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# ==================== 启动主循环 ====================

# 进入主事件循环，等待用户交互
# mainloop() 会持续监听事件（点击、按键等）
root.mainloop()