# cspell 配置说明

本仓库根目录的 `cspell.json` 是 [CSpell](https://cspell.org/)（VS Code 内置拼写检查器）的项目级配置文件。本文档说明它的**作用**以及**每个字段的含义**。

---

## 一、这个配置是做什么的

VS Code 的拼写检查器（Code Spell Checker 扩展）会扫描你打开的文本，把词典里没有的单词标上红色波浪线。这对写英文文档很实用，但 Python / Node 生态有大量**合法的技术术语**（`pyproject`、`httpx`、`isinstance`、`functools`……）不在默认英文词典里，于是被误报成"拼写错误"，视觉噪音很大、还可能淹没真正的拼写笔误。

`cspell.json` 的作用就是告诉拼写检查器：

1. **这些词是合法的**，不要再标红（`words`）
2. **这些文件/路径不用检查**，依赖目录、锁文件本来就不该查（`ignorePaths`）
3. **这类文本片段直接跳过**，比如 Python 的双下划线方法名（`ignoreRegExpList`）

配置后，`basic-python/readme.md` 里那 30 多个误报会全部消失，只剩下真正的拼写问题会被标出。

> 说明：配置只影响**拼写检查的告警显示**，不改动任何代码或文档内容，纯视觉降噪，零副作用。

---

## 二、字段逐项解释

### `version`

```json
"version": "0.2"
```

CSpell 配置文件的 schema 版本。`0.2` 是当前主流版本，固定写法，不需要改。

### `language`

```json
"language": "en"
```

检查使用的语言。`en` = 英文。文档里的中文 CSpell 不检查（也检查不了），只校验其中夹杂的英文片段。

### `caseSensitive`

```json
"caseSensitive": false
```

是否区分大小写。设为 `false` 表示 `Pyproject` 和 `pyproject` 视作同一个词，避免同词不同写法重复告警。

### `words`

```json
"words": ["pyproject", "httpx", "isinstance", ...]
```

**核心字段**——自定义词典。这里列出的单词会被 CSpell 视为"已知合法词"，不再标红。本项目按类别收录了：

| 类别 | 示例 | 说明 |
|------|------|------|
| Python 工具/包名 | `pyproject` `venv` `pypi` `httpx` `pytest` `mypy` `gunicorn` `numpy` | 生态里的专有名词 |
| Python 标准库/内置 | `asyncio` `functools` `isinstance` `getattr` `frozenset` `bytearray` `deepcopy` `kwargs` | 模块名与函数名 |
| 风格术语 | `snake_case` `camelCase` `PascalCase` `Pythonic` | 命名风格相关 |
| Node/JS 生态 | `npm` `npx` `pnpm` `yarn` `node_modules` `prettier` `eslint` `vitest` `esbuild` `rollup` `dotenv` `TypeScript` `nvmrc` | 文档里做 JS 对照时出现 |
| Python 异常类 | `TypeError` `ValueError` `KeyError` `IndexError` `AttributeError` `ImportError` `FileNotFoundError` `ZeroDivisionError` `JSONDecodeError` `MyError` | 内置 + 文档自定义异常 |
| 二进制/类型 | `Uint8Array` `ArrayBuffer` `Dockerfile` `CPython` | 跨语言对照术语 |

> 后续如果文档里又出现新的合法技术词被标红，把它加进这个数组、保存即可，告警立即消失。

### `ignoreWords`

```json
"ignoreWords": []
```

与 `words` 类似但语义不同：`words` 是"认可并加入词典"；`ignoreWords` 是"看到就忽略、完全不报"。本项目未单独使用，留空。

### `ignorePaths`

```json
"ignorePaths": [
  ".venv/**",
  "node_modules/**",
  "**/uv.lock",
  "**/package-lock.json",
  "**/*.toml",
  "**/*.lock",
  ".git/**",
  "**/.python-version"
]
```

**不进行检查的文件/目录**，支持 glob 通配符：

| 规则 | 跳过原因 |
|------|----------|
| `.venv/**` | 虚拟环境，全是第三方包源码，不该查拼写 |
| `node_modules/**` | JS 依赖目录，同理 |
| `**/uv.lock`、`**/*.lock` | 锁文件，机器生成、含大量哈希与版本号 |
| `**/package-lock.json` | 同上 |
| `**/*.toml` | 配置文件（`pyproject.toml` 等），键值非自然语言 |
| `.git/**` | Git 内部文件 |
| `**/.python-version` | 只有一行版本号，无需检查 |

> `**` 表示"任意层目录"，所以 `.venv/**` 匹配 `.venv` 下任意深度的文件。

### `ignoreRegExpList`

```json
"ignoreRegExpList": [
  "/__\\w+__/g",
  "/0x[0-9a-fA-F]+/g"
]
```

**用正则匹配、匹配到的文本片段直接跳过**。每条是 `/正则/标志` 形式的字符串：

| 正则 | 作用 |
|------|------|
| `/__\w+__/g` | Python 双下划线标识符（dunder），如 `__init__`、`__name__`、`__main__`、`__all__`。这些是约定的魔法方法名，不该被当拼写错 |
| `/0x[0-9a-fA-F]+/g` | 十六进制字面量，如 `0x1A2B`、内存地址 `0x7f...` |

> 注意 JSON 里反斜杠要转义，所以正则里的 `\w` 写成 `\\w`。`g` 是全局标志，匹配整篇文档所有出现处。

### `flagWords`

```json
"flagWords": []
```

**明确禁用的词**——出现时**一定标红**（即使词典里有）。通常用于屏蔽脏话或项目禁用词。本项目没有这类需求，留空。

---

## 三、日常使用

### 怎么验证配置生效

打开 `basic-python/readme.md`，原本 `pyproject`、`httpx`、`isinstance` 等词的红色波浪线应全部消失。若仍有少量标红：

1. **若是合法术语** → 加进 `words` 数组
2. **若是真拼错** → 改正单词
3. **若是某文件不该查** → 加进 `ignorePaths`

### 新增词条的小技巧

VS Code 里光标停在红色波浪线单词上，按 `Cmd + .`（Mac）→ 选 **"Add to folder dictionary"**，会自动把词写进 `cspell.json` 的 `words`，无需手动编辑。或者直接手动编辑该文件，效果一样。

### 不想全局检查某段代码

在 Markdown 里可以用 HTML 注释控制 CSpell 跳过某段：

```
<!-- cspell:ignore inlineword -->
```

或用区域指令包裹：

```
<!-- cspell:disable -->
这段里的词都不会被检查
<!-- cspell:enable -->
```

适合临时性的、不值得入库词典的特殊术语。

---

## 四、相关链接

- 官方文档：<https://cspell.org/configuration/>
- VS Code 扩展：<https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker>
- 支持的 glob 语法：<https://github.com/mrmlnc/fast-glob>
