# Python 速通：写给有其他编程语言经验的工程师

> 以 JavaScript 为对照，帮助你快速迁移到 Python。

---

## 📖 如何阅读这份指南

这份文档面向**已经有至少一门编程语言经验**的工程师。我们不会从"什么是变量"讲起，而是假设你已经熟悉函数、类、模块、包管理等概念，重点解决 **"Python 里怎么做"** 的问题。

### 推荐学习路径

按这个顺序阅读，能最快地上手实际开发：

1. **先建立工作流** → Part I（第 0-6 章）
   - 了解 pyenv / uv / poetry 三种工具模式
   - 学会用 `uv` 创建项目、运行脚本、安装依赖
   - 理解 `pyenv` / `uv` / `venv` 的关系
   - 了解项目目录结构和跨文件引用方式
   - **学会阅读任何 Python 项目的通用方法**

2. **理解核心语言** → 第 6-9 章（Part II）
   - 数据类型、变量、可变性
   - 迭代、枚举、推导式
   - 错误处理

3. **查阅速查表** → 第 10 章（Part III）
   - 与 JavaScript 的语法对照

---

## ⚠️ 高频坑点（先看一眼，少踩无数坑）

| # | 坑 | 正确做法 |
|---|----|----------|
| 1 | `list = [1,2,3]` | ❌ 用内置函数名做变量 → 后面 `list()` 炸掉 |
| | | ✅ 用 `items`、`data`、`names` 等描述性名字 |
| 2 | `set = {1,2,3}` | ❌ 同样遮蔽 `set()` |
| | | ✅ 用 `tags`、`unique_ids` 等 |
| 3 | `frozenset = frozenset({...})` | ❌ 赋值号右边 `frozenset(...)` 被当成未初始化的局部变量 |
| | | ✅ 变量改名 `frozen = frozenset({...})` |
| 4 | `my_set[0]` | ❌ set 无序，不支持索引 |
| | | ✅ `value in my_set` 判断成员 / `for v in my_set` 遍历 |
| 5 | Tab 和空格混用缩进 | ❌ Python 禁止混用，直接 `IndentationError` |
| | | ✅ 统一用 4 空格，配 `"editor.insertSpaces": true` |
| 6 | `import my-package` | ❌ Python 把 `-` 当减号 |
| | | ✅ 包名用下划线 `import my_package`（目录同理） |
| 7 | 可变对象做默认参数 | ❌ `def f(lst=[])` 所有调用共享同一个列表 |
| | | ✅ `def f(lst=None): if lst is None: lst = []` |
| 8 | `.venv/` 没激活就装包 | ❌ `pip install xxx` 装到了系统 Python |
| | | ✅ 用 `uv add xxx` / `uv run`，永远不用手动激活 |

> 详细说明见各章：坑 1-4 → [第 6 章](part2-language/06-data-types.md) · 坑 5 → [第 10 章](part3-appendix/10-cheatsheet.md) · 坑 6 → [第 4 章](part1-workflow/04-imports.md) · 坑 7 → [第 10 章](part3-appendix/10-cheatsheet.md) · 坑 8 → [第 2 章](part1-workflow/02-toolchain.md)

---

## 📑 目录

### Part I：先跑起来 —— 建立 Python 项目工作流

| 章节 | 内容 | 链接 |
|------|------|------|
| 0 | pyenv / uv / poetry 三种工作模式 | [阅读](part1-workflow/00-tool-modes.md) |
| 1 | 完整开发路径：从 0 到运行 | [阅读](part1-workflow/01-quickstart.md) |
| 2 | Python 开发方式与工具链（pyenv/uv/venv） | [阅读](part1-workflow/02-toolchain.md) |
| 3 | 项目常见目录结构 | [阅读](part1-workflow/03-project-structure.md) |
| 4 | 跨目录/跨文件/跨项目引用 | [阅读](part1-workflow/04-imports.md) |
| 5 | 项目初始化与部署 | [阅读](part1-workflow/05-init-deploy.md) |
| 6 | 如何阅读一个 Python 项目 | [阅读](part1-workflow/06-read-project.md) |

### Part II：语言核心 —— 理解 Python 语言本身

| 章节 | 内容 | 链接 |
|------|------|------|
| 6 | 数据类型对照 | [阅读](part2-language/06-data-types.md) |
| 7 | 变量、赋值与可变性 | [阅读](part2-language/07-variables.md) |
| 8 | 可迭代对象与枚举 | [阅读](part2-language/08-iterables.md) |
| 9 | 错误捕获 | [阅读](part2-language/09-errors.md) |
| 11 | 模块导入规则与标准库速览 | [阅读](part2-language/11-standard-library.md) |

### Part III：附录 —— 速查与工具链汇总

| 章节 | 内容 | 链接 |
|------|------|------|
| 10 | 更多差异速查（与 JS 对照） | [阅读](part3-appendix/10-cheatsheet.md) |

---

## 📝 文档约定

- 示例中 `JS:` 表示 JavaScript 写法，`Python:` 表示 Python 写法。
- 章节中带 ⚠️ 的为**常见坑点**，建议重点看。
- 带 ✅ 的为推荐做法。
- 每章末尾有「本节要点」，适合快速复习。

---

## 🔗 快速导航

- [0. 如何阅读这份指南](00-introduction.md)
- [Part I 完整内容](part1-workflow/)
- [Part II 完整内容](part2-language/)
- [Part III 完整内容](part3-appendix/)
