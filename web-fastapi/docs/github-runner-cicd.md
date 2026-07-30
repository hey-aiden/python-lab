# GitHub Actions Self-Hosted Runner 完整指南

> 从 GitHub 配置 Runner → 云服务器安装 → CI/CD Workflow 触发，一步步搭建自动化部署流水线。

---

## 目录

1. [概念 overview](#1-概念-overview)
2. [GitHub 端：注册 Runner](#2-github-端注册-runner)
3. [云服务端：安装 Runner 软件](#3-云服务端安装-runner-软件)
4. [配置 CI/CD Workflow 触发](#4-配置-cicd-workflow-触发)
5. [完整示例：FastAPI 项目自动部署](#5-完整示例fastapi-项目自动部署)
6. [Runner 管理 & 运维](#6-runner-管理--运维)
7. [常见问题排查](#7-常见问题排查)

---

## 1. 概念 overview

| 类型 | 谁提供机器 | 适用场景 |
|------|----------|---------|
| **GitHub-Hosted Runner** | GitHub 提供，用完销毁 | 公开仓库免费，私有仓库有额度 |
| **Self-Hosted Runner** | 你自己的机器（物理机/VM/容器） | 需要访问内网、特定硬件、降低成本 |

本文重点讲 **Self-Hosted Runner**，即你自己在云服务器上运行 Runner 程序，让它接收 GitHub 下发的 Job。

```
GitHub Repo ──push/PR触发──→ Workflow ──下发 Job──→ 你的云服务器（Runner）
                                                          │
                                                    执行: build → test → deploy
```

---

## 2. GitHub 端：注册 Runner

### 2.1 选择 Runner 级别

Runner 可绑定在三个级别：

| 级别 | 路径 | 适用场景 |
|------|------|---------|
| **Repository** | `Settings → Actions → Runners` | 单仓库专用 |
| **Organization** | 组织 `Settings → Actions → Runners` | 多仓库共享 |
| **Enterprise** | 企业管理后台 | 全公司共享 |

> 💡 学习/小项目选 Repository 级别即可，管理最简单。

### 2.2 添加 Self-Hosted Runner

1. 打开 GitHub 仓库 → **Settings** → **Actions** → **Runners**
2. 点击 **New self-hosted runner**
3. 选择操作系统和架构（如 Linux x64）
4. 你会看到类似这样的命令（**先在页面上留着，等服务器准备好再粘贴执行**）：

> **⚠️ 关键警告：下载链接和校验码必须从同一个 GitHub 页面复制！**
>
> GitHub 每次更新 Runner 版本，URL 中的版本号（如 `v2.336.0`）和 SHA256 校验码都会一起变。如果从文档复制了旧版本的链接、却从页面复制了新版本的校验码（或反过来），校验一定会失败。
>
> **正确做法：去 `Settings → Actions → Runners → New self-hosted runner`，把页面上的 `Download` 和 `Check` 两段命令一起复制，不要混搭。**

```bash
# 创建 runner 目录
mkdir actions-runner && cd actions-runner

# 下载 runner 软件包（⚠️ 版本号以 GitHub 页面为准，这里是示例）
curl -o actions-runner-linux-x64-<VERSION>.tar.gz -L \
  https://github.com/actions/runner/releases/download/v<VERSION>/actions-runner-linux-x64-<VERSION>.tar.gz

# 校验（⚠️ 校验码也必须来自页面，和下载链接同版本）
echo "<页面上的校验码>  actions-runner-linux-x64-<VERSION>.tar.gz" | shasum -a 256 -c

# 解压（校验通过再解压）
tar xzf ./actions-runner-linux-x64-<VERSION>.tar.gz
```

> 💡 有时候下载断了，文件实际是空的或不完整，校验也会报 `FAILED`。先 `ls -lh` 看看文件大小是否 > 100MB，如果只有几 KB 就重新 `curl` 下载。

### 2.3 Token 时效性

- **注册 token**：1 小时有效，仅用于 `./config.sh` 这一步
- **配置完成后**：Runner 会自动生成长期凭证，token 过期不影响已注册的 Runner
- 如果 `./config.sh` 超时了，回到页面重新生成一个 token 即可

---

## 3. 云服务端：安装 Runner 软件

### 3.1 选择云服务器

| 云厂商 | 最低推荐配置 | 参考价格 |
|--------|------------|---------|
| **AWS EC2** | t3.medium (2vCPU, 4GB) | ~$0.04/h |
| **阿里云 ECS** | 2vCPU, 4GB | ~¥0.2/h |
| **腾讯云 CVM** | 2核 4GB | ~¥0.2/h |
| **GCP Compute Engine** | e2-medium | ~$0.03/h |
| **Azure VM** | B2s (2vCPU, 4GB) | ~$0.04/h |

> 💡 构建 Python/FastAPI 项目 2vCPU+4GB 足够；Node/Go 编译也够用；Docker 构建建议 4GB+ 内存。

### 3.2 服务器基础环境配置

以 Ubuntu 22.04 为例，SSH 登录后先做基础配置：

```bash
# 1. 系统更新
sudo apt update && sudo apt upgrade -y

# 2. 安装基础工具
sudo apt install -y curl wget git build-essential

# 3. 安装 Python（FastAPI 项目用）
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# 4. 安装 uv（Python 包管理器）
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.cargo/env

# 5. 安装 Docker（如果构建/部署需要）
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# 退出重登使 docker 组生效

# 6. 创建 runner 专用用户（安全最佳实践）
sudo useradd -m -s /bin/bash github-runner
sudo usermod -aG docker github-runner   # 如果需要 docker
```

### 3.3 下载并配置 Runner

切到 runner 用户或你自己的用户，执行 GitHub 页面给你的命令：

```bash
# 切到 runner 目录（⚠️ 版本号以 GitHub 页面为准，这里是示例）
mkdir ~/actions-runner && cd ~/actions-runner
curl -o actions-runner-linux-x64-<VERSION>.tar.gz -L \
  https://github.com/actions/runner/releases/download/v<VERSION>/actions-runner-linux-x64-<VERSION>.tar.gz
tar xzf ./actions-runner-linux-x64-<VERSION>.tar.gz

# 验证解压成功（应该看到 config.sh、run.sh 等文件）
ls -la

# 配置 runner（交互式）
./config.sh --url https://github.com/<YOUR_ORG>/<YOUR_REPO> \
             --token <FROM_GITHUB_PAGE>
```

> ⚠️ **如果报 `No such file or directory`，按以下步骤排查：**
>
> ```bash
> # 1. 确认你在正确的目录
> pwd                          # 应该显示 ~/actions-runner
> cd ~/actions-runner          # 不在的话切过去
>
> # 2. 确认 tar 包下载成功
> ls -lh ~/actions-runner-*.tar.gz   # 文件大小应该 > 100MB
>
> # 3. 确认解压成功（应该看到很多文件）
> ls -la ~/actions-runner/
> # 正常输出包含: config.sh  run.sh  svc.sh  bin/  externals/
>
> # 4. 如果目录是空的 → 重新解压
> tar xzf ~/actions-runner-linux-x64-*.tar.gz -C ~/actions-runner/
>
> # 5. 如果 tar 包也没有 → 重新下载（去 GitHub Settings → Actions → Runners 复制最新链接）
> ```
>
> 最常犯的错误：**下载了 tar.gz 但忘记解压**，或者下载失败（curl 因为网络问题只下了一个空文件）。

`./config.sh` 交互式问答：

```
Enter the name of the runner group (default): [直接回车]
Enter the name of the runner: [my-cloud-runner]       # 起个好认的名字
Enter any extra labels: [deploy,fastapi]              # 可选标签，workflow 用 runs-on 匹配
Enter name of work folder: [直接回车]
```

### 3.4 安装为系统服务（保持运行）

**关键步骤** — 不装成服务的话，SSH 断开 Runner 就停了。

```bash
# 安装并启动服务
sudo ./svc.sh install
sudo ./svc.sh start

# 检查状态
sudo ./svc.sh status
```

> 如果用的是 `github-runner` 专用用户，记得先 `sudo -u github-runner ./config.sh` 再用 `sudo ./svc.sh install`。

安装后服务定义为 `/etc/systemd/system/actions.runner.*.service`，你也能用 `systemctl` 管理：

```bash
sudo systemctl status actions.runner.*
sudo systemctl restart actions.runner.*
```

### 3.5 验证 Runner 在线

回到 GitHub：**Settings → Actions → Runners**，你应该看到：

```
✅ my-cloud-runner
   Idle | labels: self-hosted, Linux, x64, deploy, fastapi
```

状态从 `Offline` 变成 `Idle` 就说明连接成功。

### 3.6 卸载 Runner

```bash
cd ~/actions-runner
sudo ./svc.sh stop
sudo ./svc.sh uninstall
./config.sh remove --token <REMOVAL_TOKEN>   # 去 GitHub 页面拿 removal token
```

---

## 4. 配置 CI/CD Workflow 触发

### 4.1 触发事件一览

| 事件 | 触发时机 | 典型用途 |
|------|---------|---------|
| `push` | 推送代码到分支 | 触发构建/测试 |
| `pull_request` | 创建/更新 PR | PR 检查 |
| `workflow_dispatch` | 手动触发（Web UI / API） | 手动部署 |
| `schedule` | cron 定时任务 | 夜间构建、定时任务 |
| `release` | 发布/预发布 | 发布时构建部署 |
| `workflow_run` | 另一个 workflow 完成后 | 流水线串联 |

### 4.2 基础 Push 触发

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'src/**'          # 只有 src/ 下文件变更才触发
      - 'pyproject.toml'
      - '.github/workflows/**'
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: self-hosted     # 使用你自己的 runner
    # runs-on: [self-hosted, deploy, fastapi]  # 用标签精确匹配

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        run: uv run pytest -v

      - name: Run lint
        run: uv run ruff check src/
```

### 4.3 手动触发部署

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  workflow_dispatch:           # 纯手动触发
    inputs:
      environment:
        description: '部署环境'
        required: true
        type: choice
        options: [staging, production]
        default: staging

jobs:
  deploy:
    runs-on: [self-hosted, deploy]
    environment: ${{ inputs.environment }}

    steps:
      - uses: actions/checkout@v4

      - name: Deploy
        run: |
          echo "Deploying to ${{ inputs.environment }}..."
          # 在这里写部署命令
```

### 4.4 定时任务

```yaml
on:
  schedule:
    # 每天 UTC 2:00（北京时间 10:00）运行
    - cron: '0 2 * * *'
    # 每周一 9:00 UTC
    - cron: '0 9 * * 1'
```

### 4.5 条件触发（按分支/路径/标签）

```yaml
on:
  push:
    branches:
      - main
      - 'release/**'         # release/ 下所有分支
    tags:
      - 'v*'                 # 推送 v1.0.0 等 tag 时触发
    paths-ignore:            # 以下路径变更不触发
      - 'docs/**'
      - '*.md'
      - '.github/ISSUE_TEMPLATE/**'
```

### 4.6 多 Job 串联

```yaml
jobs:
  test:
    runs-on: self-hosted
    outputs:
      test_status: ${{ job.status }}
    steps: [...]

  build:
    needs: test              # test 通过后才执行
    runs-on: self-hosted
    steps: [...]

  deploy:
    needs: build
    runs-on: self-hosted
    if: github.ref == 'refs/heads/main'   # 只在 main 分支部署
    environment: production
    steps: [...]
```

### 4.7 子目录项目（Monorepo）：Repo 根目录 vs 子目录

你的项目结构很可能像这样：

```
python-lab/                  ← Git 仓库根目录（GitHub 上 checkout 出来的位置）
├── .github/workflows/       ← ⚠️ Workflow 文件必须放在这里（仓库根目录下）
│   ├── ci.yml
│   └── cd.yml
├── web-fastapi/             ← 实际要部署的子项目
│   ├── pyproject.toml
│   ├── src/
│   └── Dockerfile
├── guide-python/            ← 其他子项目（无关）
└── old-version/
```

**关键点：Workflow 文件位置是固定的，命令执行可以切到任意子目录。**

| 你关心的 | 答案 |
|----------|------|
| Repo 根目录需要配什么？ | 只需要 `.github/workflows/*.yml`，别的什么都不用 |
| Runner 需要特殊配置吗？ | 不需要，Runner 只管执行 workflow 里的命令 |
| 怎么让命令在子目录执行？ | 以下三种方式任选 |

**方式一：每个 step 里 `cd`（显式，推荐新手）**

```yaml
steps:
  - uses: actions/checkout@v4          # checkout 整个仓库到 $GITHUB_WORKSPACE

  - name: Install dependencies
    run: |
      cd web-fastapi                    # 切到子目录
      uv sync

  - name: Run tests
    run: |
      cd web-fastapi
      uv run pytest -v
```

**方式二：`working-directory` 每个 step 指定（适合少量步骤）**

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Install dependencies
    working-directory: web-fastapi
    run: uv sync

  - name: Run tests
    working-directory: web-fastapi
    run: uv run pytest -v
```

**方式三：`defaults.run` 全局设置（最干净，推荐）**

```yaml
defaults:
  run:
    working-directory: web-fastapi      # 所有 run 命令默认在此目录执行

jobs:
  test:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: uv sync                    # 无需 cd，自动在 web-fastapi/ 下执行

      - name: Run tests
        run: uv run pytest -v

      - name: Type check
        run: uv run mypy src/
```

> ⚠️ `working-directory` 只对 `run:` 生效，`uses:`（如 `actions/checkout@v4`）不受影响，checkout 始终在 `$GITHUB_WORKSPACE` 即 repo 根目录。

**路径过滤也要加子目录前缀：**

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'web-fastapi/**'            # 只有 web-fastapi/ 变了才触发
      - '.github/workflows/**'      # workflow 本身变了也触发
```

---

## 5. 完整示例：FastAPI 项目自动部署

以下是对应 `web-fastapi/` 子目录项目的完整 CI/CD 配置。

### 5.1 CI：测试 + 类型检查（push 到任意分支）

```yaml
# .github/workflows/ci.yml   ← 文件位置：repo 根目录/.github/workflows/
name: CI

on:
  push:
    branches: [main]
    paths:
      - 'web-fastapi/**'
  pull_request:
    branches: [main]
    paths:
      - 'web-fastapi/**'

defaults:
  run:
    working-directory: web-fastapi     # 所有步骤默认在此目录执行

jobs:
  test:
    runs-on: self-hosted
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Install dependencies
        run: uv sync                     # 自动在 web-fastapi/ 下执行

      - name: Run tests
        run: uv run pytest -v --tb=short

      - name: Type check
        run: uv run mypy src/ --ignore-missing-imports
```

### 5.2 CD：Docker 构建 + 部署（push 到 main）

```yaml
# .github/workflows/cd.yml
name: CD

on:
  push:
    branches: [main]
    paths:
      - 'web-fastapi/**'
      - '.github/workflows/cd.yml'

defaults:
  run:
    working-directory: web-fastapi

jobs:
  build-and-deploy:
    runs-on: [self-hosted, deploy]
    environment: production

    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: |
          docker build -t fastapi-app:latest .
          docker tag fastapi-app:latest fastapi-app:$(git rev-parse --short HEAD)

      - name: Deploy
        run: |
          docker compose down
          docker compose up -d

      - name: Health check
        run: |
          sleep 3
          curl -f http://localhost:8000/health || exit 1
```

### 5.3 手动部署（staging ↔ production 切换）

```yaml
# .github/workflows/manual-deploy.yml
name: Manual Deploy

on:
  workflow_dispatch:
    inputs:
      env:
        description: 'Target environment'
        required: true
        type: choice
        options: [staging, production]

defaults:
  run:
    working-directory: web-fastapi

jobs:
  deploy:
    runs-on: [self-hosted, deploy]
    environment: ${{ inputs.env }}

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to ${{ inputs.env }}
        run: |
          docker compose -f docker-compose.${{ inputs.env }}.yml up -d --build
```

### 5.4 最终的文件结构

```
python-lab/                          ← Repo 根目录
├── .github/
│   └── workflows/
│       ├── ci.yml                   ← CI：测试 + 类型检查
│       ├── cd.yml                   ← CD：自动部署
│       └── manual-deploy.yml        ← 手动部署
├── web-fastapi/                     ← 子项目（不额外配置，workflow 已指向这里）
│   ├── pyproject.toml
│   ├── src/
│   ├── Dockerfile
│   └── docker-compose.yml
├── guide-python/                    ← 其他子项目，不触发部署
└── CLAUDE.md
```

---

## 6. Runner 管理 & 运维

### 6.1 安全注意事项

| 问题 | 对策 |
|------|------|
| **公开仓库的 PR 可以执行任意代码** | **公开仓库不要用 self-hosted runner 跑 PR**，或启用 `Require approval` |
| **Runner 能访问你的服务器** | 用 `github-runner` 专用用户，限制 `sudo` 权限 |
| **敏感环境变量泄露** | 用 GitHub Secrets + Environment Protection Rules |
| **Runner 令牌泄露** | 定期轮换，不要硬编码到代码中 |

**公开仓库的紧急设置**：

```
Settings → Actions → Runners → 勾选
  ☑ Require approval for all outside collaborators
```

### 6.2 Runner 自动更新

Runner 软件不会自动更新，需要手动升级。但可以用 scheduled workflow 来提醒：

```yaml
# .github/workflows/check-runner-version.yml
on:
  schedule:
    - cron: '0 3 * * 1'  # 每周一检查

jobs:
  check:
    runs-on: self-hosted
    steps:
      - name: Check runner version
        run: |
          echo "Current runner version:"
          ~/actions-runner/config.sh --version
          echo "Latest: https://github.com/actions/runner/releases/latest"
```

### 6.3 资源清理

Runner 运行久了会积累磁盘垃圾（Docker 镜像、缓存等）：

```bash
# 定期清理 Docker（加到 crontab 或 scheduled workflow）
docker system prune -af --volumes --filter "until=168h"
```

放到 workflow 里定期跑：

```yaml
on:
  schedule:
    - cron: '0 4 * * 0'   # 每周日 4:00 UTC

jobs:
  cleanup:
    runs-on: self-hosted
    steps:
      - name: Docker cleanup
        run: docker system prune -af --volumes --filter "until=168h"
```

### 6.4 监控 Runner 状态

GitHub 提供 API 查询 Runner 状态：

```bash
# 列出所有 self-hosted runner
gh api repos/:owner/:repo/actions/runners

# 检查特定 runner 是否在线
gh api repos/:owner/:repo/actions/runners \
  --jq '.runners[] | select(.name=="my-cloud-runner") | .status'
```

---

## 7. 常见问题排查

### 7.1 Runner 离线 (Offline)

```bash
# 检查服务是否在运行
sudo systemctl status actions.runner.*

# 查看 runner 日志
journalctl -u actions.runner.* -f

# 查看 runner 自身日志
cat ~/actions-runner/_diag/*.log

# 重启服务
sudo systemctl restart actions.runner.*
```

常见原因：
- 服务器重启后服务没自动启动 → `sudo ./svc.sh start`
- 网络问题，服务器无法访问 GitHub → `curl -I https://github.com`
- Runner token 过期（按 60 天轮换）→ 去 GitHub 页面重新生成
- 磁盘满了 → `df -h`

### 7.2 Job 一直 Queued 不开始

- Runner 可能正在执行另一个 Job（Self-hosted runner 默认并发=1）
- Runner 的 labels 和 workflow 的 `runs-on` 不匹配
- Runner 状态是 `Offline`

### 7.3 Job Failed 但本地能跑

```yaml
# 先加调试步骤
- name: Debug environment
  run: |
    whoami
    pwd
    ls -la
    python3 --version
    docker --version
    env | sort
```

常见原因：环境变量缺失、Python 版本不一致、缺少系统依赖、Docker 组没加对。

### 7.4 `./config.sh` 报 SSL 错误

云服务器时区或时间不准导致：

```bash
# 同步系统时间
sudo timedatectl set-ntp on
sudo timedatectl set-timezone Asia/Shanghai
```

### 7.5 权限问题

```bash
# 如果 runner 用户权限不够
sudo usermod -aG docker $USER          # docker 权限
sudo chown -R $USER:$USER ~/actions-runner  # runner 目录权限
```

---

## 附录：多 Runner + Label 策略示例

当项目变多或团队变大，用 Label 精准路由 Job：

```
Runner 实例            Labels
─────────────────────────────────────────────
build-server-01       self-hosted, linux, x64, build, 16gb
deploy-server-01      self-hosted, linux, x64, deploy, production
test-runner-01        self-hosted, linux, x64, test, lightweight
```

Workflow 匹配：

```yaml
# 轻量级测试随便哪台都行
runs-on: self-hosted

# 构建需要大内存
runs-on: [self-hosted, build, 16gb]

# 只部署到生产环境
runs-on: [self-hosted, deploy, production]
```

---

## 参考链接

- [GitHub Actions Runner 官方文档](https://docs.github.com/en/actions/hosting-your-own-runners)
- [Runner 软件 Releases](https://github.com/actions/runner/releases)
- [Workflow 语法参考](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub Actions 安全加固](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
