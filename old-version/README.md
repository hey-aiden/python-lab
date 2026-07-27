# Python 

Python 起步仓库。

## 环境要求

- Python 3.9.6+（系统自带）
- uv 0.10.12+（Python 包管理器）

## 项目结构

```
.
├── pyproject.toml      # 项目配置和依赖声明
├── uv.lock             # 依赖锁定文件
├── Makefile            # 任务运行脚本
├── .venv/              # 虚拟环境（自动生成）
│   ├── bin/            # 可执行文件（python, pip 等）
│   └── lib/python3.9/site-packages/  # 依赖安装目录
├── TROUBLESHOOTING.md  # 问题排查文档
└── *.py                # Python 脚本
```

## 依赖安装目录

依赖安装在虚拟环境目录下：

```
.venv/lib/python3.9/site-packages/
├── mysql/                          # mysql-connector-python 包
├── mysql_connector_python-9.4.0.dist-info/  # 包元信息
└── ...
```

**查看已安装的依赖：**
```bash
uv pip list

# 或直接查看目录
ls .venv/lib/python3.9/site-packages/
```

## 依赖管理

### 安装依赖
```bash
uv sync
```

### 添加新依赖
```bash
uv add <package>

# 使用国内镜像
uv add <package> -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 移除依赖
```bash
uv remove <package>
```

### 当前依赖
- `mysql-connector-python` - MySQL 数据库连接器

## 运行方式

### 方式 1：uv run（推荐）
```bash
uv run mysql_demo.py
```

### 方式 2：Makefile
```bash
make run
```

### 方式 3：手动激活虚拟环境
```bash
source .venv/bin/activate
python mysql_demo.py
deactivate
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `uv run <script.py>` | 运行脚本 |
| `uv add <package>` | 添加依赖 |
| `uv remove <package>` | 移除依赖 |
| `uv sync` | 同步依赖 |
| `uv pip list` | 查看已安装的包 |
| `make run` | 运行 mysql_demo.py |

## 配置文件说明

### pyproject.toml
项目配置文件，类似 Node.js 的 `package.json`：
- 定义项目元信息
- 声明项目依赖
- 配置开发工具

### uv.lock
依赖锁定文件，确保依赖版本一致（类似 `package-lock.json`）。

### Makefile
任务运行脚本，类似 npm scripts：
```makefile
.PHONY: run demo

run:
	uv run mysql_demo.py

demo:
	uv run other_script.py
```

## 遇到问题？

查看 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) 获取常见问题解决方案。