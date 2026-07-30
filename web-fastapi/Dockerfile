# ---- 构建阶段 ----
FROM python:3.11-slim AS builder

WORKDIR /app

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 先复制依赖文件，利用 Docker 层缓存
COPY pyproject.toml uv.lock ./

# 安装依赖到虚拟环境（不安装 dev 依赖）
RUN uv sync --frozen --no-dev --no-editable

# ---- 运行阶段 ----
FROM python:3.11-slim

WORKDIR /app

# 从 builder 复制虚拟环境
COPY --from=builder /app/.venv /app/.venv

# 复制源代码
COPY src/ /app/src/

# 从 builder 复制 uv（用于 uv run）
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv

# 暴露端口
EXPOSE 8000

# 启动命令：uv run 自动使用 .venv 中的虚拟环境
CMD ["uv", "run", "run"]
