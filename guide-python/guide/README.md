# Python 速通：写给有其他编程语言经验的工程师

> 以 JavaScript 为对照，帮助你快速迁移到 Python。

---

## 📖 如何阅读这份指南

这份文档面向**已经有至少一门编程语言经验**的工程师。我们不会从"什么是变量"讲起，而是假设你已经熟悉函数、类、模块、包管理等概念，重点解决 **"Python 里怎么做"** 的问题。

### 推荐学习路径

按这个顺序阅读，能最快地上手实际开发：

1. **先建立工作流** → Part I（第 0-5 章）
   - 了解 pyenv / uv / poetry 三种工具模式
   - 学会用 `uv` 创建项目、运行脚本、安装依赖
   - 理解 `pyenv` / `uv` / `venv` 的关系
   - 了解项目目录结构和跨文件引用方式

2. **理解核心语言** → 第 6-9 章（Part II）
   - 数据类型、变量、可变性
   - 迭代、枚举、推导式
   - 错误处理

3. **查阅速查表** → 第 10 章（Part III）
   - 与 JavaScript 的语法对照

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

### Part II：语言核心 —— 理解 Python 语言本身

| 章节 | 内容 | 链接 |
|------|------|------|
| 6 | 数据类型对照 | [阅读](part2-language/06-data-types.md) |
| 7 | 变量、赋值与可变性 | [阅读](part2-language/07-variables.md) |
| 8 | 可迭代对象与枚举 | [阅读](part2-language/08-iterables.md) |
| 9 | 错误捕获 | [阅读](part2-language/09-errors.md) |

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
