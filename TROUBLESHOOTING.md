# Python 环境问题排查与解决方案

> 2026-03-23

## 问题 1：uv add 报错 - No pyproject.toml found

### 错误信息
```
error: No `pyproject.toml` found in current directory or any parent directory
```

### 原因
`uv add` 是往项目里添加依赖，需要 `pyproject.toml` 文件（类似 npm 的 `package.json`）。

### 解决方案

**方式 1：创建项目后使用 uv add**
```bash
uv init
uv add mysql-connector-python
```

**方式 2：创建虚拟环境后使用 uv pip install（推荐用于学习仓库）**
```bash
uv venv
source .venv/bin/activate
uv pip install <package>
```

---

## 问题 2：PyPI 连接超时

### 错误信息
```
error: Request failed after 3 retries in 52.1s
  Caused by: Failed to fetch: `https://pypi.org/simple/xxx/`
  Caused by: operation timed out
```

### 原因
国内访问 PyPI 官方源速度慢或无法访问。

### 解决方案
使用国内镜像源：

```bash
# 清华镜像（推荐）
uv pip install <package> -i https://pypi.tuna.tsinghua.edu.cn/simple

# 阿里云镜像
uv pip install <package> -i https://mirrors.aliyun.com/pypi/simple/

# 腾讯云镜像
uv pip install <package> -i https://mirrors.cloud.tencent.com/pypi/simple/
```

### 配置默认镜像源
```bash
# 设置全局默认镜像
uv pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 问题 3：pyenv 残留配置导致终端报错

### 原因
卸载 pyenv 后，`~/.zshrc` 中的配置没有清理，每次打开终端都会尝试初始化不存在的 pyenv。

### 解决方案
删除 `~/.zshrc` 中的 pyenv 相关配置：
```bash
# 以下几行需要删除
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
```

---

## 问题 5：MySQL 操作 "Unread result found"

### 错误信息
```
mysql.connector.errors.InternalError: Unread result found
```

### 原因
在同一个 cursor 上，前一个 SELECT 语句的结果没有被消费完，就执行了下一个 SQL 语句。

### 解决方案
先消费完 SELECT 结果，再执行下一个语句：
```python
# 错误写法
cursor.execute("SELECT * FROM table")
cursor.execute("INSERT INTO table ...")  # 报错！

# 正确写法
cursor.execute("SELECT * FROM table")
records = cursor.fetchall()  # 先消费结果
cursor.execute("INSERT INTO table ...")  # 再执行下一条
```

---

## 问题 6：INSERT/UPDATE/DELETE 不生效

### 原因
MySQL 默认自动提交关闭，需要手动 `commit()` 提交事务。

### 解决方案
```python
cursor.execute("INSERT INTO table ...")
DB.commit()  # 必须提交事务！
print(f"影响行数: {cursor.rowcount}")
```

---

## 问题 7：cursor 和 connection 关闭顺序

### 原因
cursor 依赖 connection，如果先关闭 connection，再关闭 cursor 会出错。

### 解决方案
```python
# 正确顺序
cursor.close()  # 先关游标
DB.close()      # 再关连接
```

---

## 问题 4：文件名与模块名冲突

### 错误信息
```
ModuleNotFoundError: No module named 'mysql.connector'; 'mysql' is not a package
```

### 原因
当前目录下的 Python 文件名（如 `mysql.py`）与要导入的第三方包模块名相同，Python 导入时会优先找到当前目录的文件，而不是已安装的包。

### 解决方案
重命名冲突的文件：
```bash
mv mysql.py mysql_demo.py
```

### 避免方法
- 不要用 Python 标准库或常用第三方包的名称作为文件名
- 常见冲突名称：`mysql.py`、`email.py`、`json.py`、`time.py`、`random.py` 等

---

## 问题 5：找不到 python 命令

### 错误信息
```
python: command not found
```

### 原因
macOS 默认只有 `python3`，没有 `python` 命令。之前可能由 pyenv 提供 `python` shim，卸载后就没了。

### 解决方案

**方式 1：使用 python3**
```bash
python3 your_script.py
```

**方式 2：使用 uv 管理 Python**
```bash
uv python install 3.12
uv python pin 3.12
```

---

## 当前环境配置

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.9.6 | 系统自带（Command Line Tools） |
| uv | 0.10.12 | Python 包管理器（Homebrew 安装） |
| pyenv | 已删除 | 不再使用 |

---

## 常用命令速查

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate

# 安装包（使用国内镜像）
uv pip install <package> -i https://pypi.tuna.tsinghua.edu.cn/simple

# 查看已安装的包
uv pip list

# 退出虚拟环境
deactivate
```

---

## 问题 8：macOS 上 tkinter GUI 程序崩溃

### 错误信息
```
macOS 26 (2603) or later required, have instead 16 (1603) !
abort python3 gui_simple.py
```
或只显示"Python 意外退出"，看不到具体错误。

### 原因
macOS 系统自带的 Python（Command Line Tools）包含的 Tcl/Tk 版本过旧，与当前 macOS 版本不兼容，导致 GUI 程序无法运行。

### 解决方案

**方式 1：使用 uv 安装新版 Python（推荐）**
```bash
# 安装新版 Python（自带新版 Tcl/Tk）
uv python install 3.12

# 设置项目使用的 Python 版本
uv python pin 3.12

# 运行 GUI 程序
uv run gui_simple.py
```

**方式 2：使用 Homebrew 安装 python-tk**
```bash
brew install python-tk@3.12
python3.12 gui_simple.py
```

### 注意事项
- `uv python pin 3.12` 只对 `uv run` 命令生效
- 直接运行 `python --version` 仍会显示系统 Python 版本
- 查看项目使用的 Python 版本：`uv run python --version`

---

## 问题 9：uv pin 后 python --version 不变

### 错误现象
```bash
uv python pin 3.12
python --version  # 仍然显示 3.9.6
```

### 原因
`uv python pin` 设置的是项目级别的 Python 版本，只对 `uv run` 命令生效。直接运行 `python` 命令使用的是系统 PATH 中的 Python。

### 解决方案
```bash
# 查看项目使用的 Python 版本
uv run python --version

# 或查看 .python-version 文件
cat .python-version

# 运行脚本
uv run your_script.py
```
