# Docker Build 错误记录

## 错误现象

```bash
docker build -t web-fastapi .
```

```
RUN uv sync --frozen --no-dev --no-editable
OSError: Readme file does not exist: README.md
```

`docker build` 成功后再 `docker run` 同样报错：
```
OSError: Readme file does not exist: README.md
```

## 根因分析

### 触发链条

```
1. pyproject.toml 声明 readme = "README.md"
     ↓
2. .dockerignore 中 *.md 排除所有 .md 文件
     ↓
3. Dockerfile 没有 COPY README.md 进入镜像
     ↓
4. uv sync / uv run 处理 pyproject.toml 元数据时，检查 readme 文件是否存在
     ↓
5. 文件不存在 → OSError
```

### 为什么 `uv` 需要 `README.md`

`pyproject.toml` 中 `readme = "README.md"` 是 [PEP 621](https://peps.python.org/pep-0621/) 定义的项目元数据字段，用于 PyPI 打包时展示项目说明。`uv` 和 `hatchling` 在解析项目时会校验该字段指向的文件是否存在 — 不管是否真的在构建包，只要声明了就会检查。

### 为什么 `--no-editable` 会触发

`uv sync --no-editable` 执行的是**非可编辑安装**（类似 `pip install`），需要将当前项目打包成 wheel 再安装。打包过程由 `hatchling` 完成，hatchling 读取 `pyproject.toml` 的 `[project]` 元数据，发现 `readme = "README.md"`，尝试打开 → 不存在 → `OSError`。

对比 `--editable`（可编辑安装）创建符号链接指向源码目录，不经过打包步骤，不会触发。

## 修复方案（最终采用）

### 删掉 `readme` 字段 — 治本

```diff
 [project]
 name = "web-fastapi"
 version = "0.1.0"
 description = "web development - fastapi framework deploy"
-readme = "README.md"
 requires-python = ">=3.11"
```

`readme` 是**可选字段**，只用于 PyPI 包页面展示。本项目不发布到 PyPI，删除它：
- 不需要在 Docker 镜像中携带 `README.md`
- 不需要修改 `.dockerignore`
- 不需要在 `Dockerfile` 中额外 `COPY`
- `uv sync` / `uv run` 行为完全不受影响

删完后执行 `uv lock` 重新生成 lockfile。

### 为什么不用"复制 README.md"的方案

最初尝试了两个方案：

| 方案 | 做法 | 问题 |
|------|------|------|
| 复制 README.md | `.dockerignore` 加例外 + `Dockerfile` 两个阶段都 COPY | 给镜像塞了无用的文件，且 Dockerfile 每次 COPY 多一个文件 |
| **删除 readme 字段** | 删掉 `pyproject.toml` 中的 `readme` | 干净，零额外开销 |

`readme` 字段对运行时没有任何作用，声明它却要额外维护文件拷贝 — 删掉是正确选择。

## 总结

| 问题类型 | `pyproject.toml` 声明了不需要的元数据字段 |
|----------|------------------------------------------|
| 根因 | `readme = "README.md"` 声明的文件在 Docker 镜像中不存在 |
| 定位方式 | 读错误信息 → 追踪 `pyproject.toml` → 理解 PEP 621 字段用途 |
| 修复 | 删除 `pyproject.toml` 中不必要的 `readme` 字段 |

---

## 延伸：`pyproject.toml` 字段与 `uv`、`hatchling` 的构建关联

### 三个角色

```
pyproject.toml  ──声明"要什么"──→  uv  ──委托"怎么建"──→  hatchling
    (项目元数据)                  (包管理器)              (构建后端)
```

| 角色 | 职责 | 类比 |
|------|------|------|
| **pyproject.toml** | 声明项目的元数据、依赖、构建配置 | 施工图纸 |
| **uv** | 解析依赖、管理虚拟环境、调度构建 | 施工队长 |
| **hatchling** | 执行实际的构建动作（打包 wheel） | 建筑工人 |

### 执行流程

```
$ uv sync --no-editable
     │
     ▼
 1. uv 读取 pyproject.toml
     ├── [build-system] → 找到构建后端是 hatchling
     ├── [project]       → 收集元数据（name, version, readme, ...）
     └── [project.scripts] → 记录入口点
     │
     ▼
 2. uv 调用 hatchling 构建 wheel
     ├── hatchling 读取 [project] 所有字段
     ├── 遇到 readme = "README.md" → 打开文件读取内容
     ├── 遇到 license = "LICENSE"  → 同样会打开文件
     └── 打包成 .whl 文件
     │
     ▼
 3. uv 将 wheel 安装到 .venv
```

### 字段分类：哪些字段会触发文件读取

`[project]` 下的字段分为两类：

#### 纯文本字段（不触发文件读取）

声明了就直接用值，不需要打开任何文件：

```toml
[project]
name = "web-fastapi"              # 包名
version = "0.1.0"                 # 版本号
description = "..."               # 简短描述
requires-python = ">=3.11"        # Python 版本约束
dependencies = ["fastapi", ...]   # 运行时依赖
```

#### 文件引用字段（触发文件读取 ⚠️）

声明的是一个文件路径，hatchling 构建时会打开这个文件读取内容：

```toml
[project]
readme = "README.md"              # PyPI 项目说明页内容
license = "LICENSE"               # 许可证文件内容
license-files = ["LICENSE*"]      # 打包进 wheel 的许可证文件列表
```

这些字段的共同特征：它们的值是**文件路径**，hatchling 需要把文件内容嵌入到包的元数据中，所以构建时一定会去 `open()` 这个文件。文件不在就 `OSError`。

### Docker 镜像视角：你真正需要哪些

当你把项目跑在 Docker 里时，按实际需求裁剪：

| pyproject.toml 字段 | Docker 镜像需要吗？ | 为什么 |
|---------------------|---------------------|--------|
| `name` | ✅ 需要 | 包标识 |
| `version` | ✅ 需要 | 版本解析 |
| `requires-python` | ✅ 需要 | 环境校验 |
| `dependencies` | ✅ 需要 | 安装依赖 |
| `[project.scripts]` | ✅ 需要 | `uv run dev` / `uv run run` 解析入口 |
| `readme` | ❌ 不需要 | 只用于 PyPI 展示，删掉或确保文件存在 |
| `license` | ❌ 不需要 | 只用于 PyPI 展示 |
| `description` | ❌ 不需要 | 纯信息字段 |
| `authors` / `urls` | ❌ 不需要 | 纯信息字段 |

**原则：** Docker 镜像只运行，不发布。PyPI 展示类字段（`readme`、`license`、`description`）对运行时毫无影响，但声明了就要求对应文件存在。要么删掉声明，要么保证文件在镜像中。

### 本项目最后保留的字段

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "web-fastapi"              # uv 需要的标识
version = "0.1.0"                 # uv 需要的标识
requires-python = ">=3.11"        # 环境约束
dependencies = [...]              # 运行时依赖

[dependency-groups]
dev = [...]                       # 开发依赖（--no-dev 跳过）

[project.scripts]                 # uv run 入口
dev = "app.main:start"
run = "app.main:run"

[tool.hatch.build.targets.wheel]
packages = ["src/app"]            # 指定打包路径
```

没有 `readme`，没有 `license`，没有 `description` — Docker 镜像不需要它们。**`pyproject.toml` 里每多一行声明，就多一个潜在的文件依赖。**
