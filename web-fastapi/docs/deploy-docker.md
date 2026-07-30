# Docker 部署指南

> 将 web-fastapi 项目容器化部署到云服务器。

---

## 1. 本地构建 & 测试

```bash
# 构建镜像
docker build -t web-fastapi:latest .

# 本地运行测试
docker run -p 8000:8000 --rm web-fastapi:latest

# 测试接口
curl http://127.0.0.1:8000/api/v1/hello/42
```

---

## 2. 推送到云服务器

### 方式 A：推送到容器仓库（Docker Hub / 阿里云 ACR）

```bash
# 打 tag
docker tag web-fastapi:latest your-registry/web-fastapi:latest

# 推送
docker push your-registry/web-fastapi:latest

# 服务器上拉取并运行
ssh your-server
docker pull your-registry/web-fastapi:latest
docker run -d -p 8000:8000 --name web-fastapi your-registry/web-fastapi:latest
```

### 方式 B：服务器本地构建

```bash
# 打包项目（排除 .venv、__pycache__ 等）
rsync -avz --exclude '.venv' --exclude '__pycache__' --exclude 'assets' \
  ./web-fastapi/ your-server:~/web-fastapi/

# ssh 到服务器构建
ssh your-server
cd ~/web-fastapi
docker build -t web-fastapi:latest .
docker run -d -p 8000:8000 --restart=always --name web-fastapi web-fastapi:latest
```

---

## 3. 持久化运行

```bash
# --restart=always  容器崩溃或服务器重启后自动恢复
# -d                后台运行
docker run -d \
  --restart=always \
  -p 8000:8000 \
  --name web-fastapi \
  web-fastapi:latest

# 查看日志
docker logs -f web-fastapi
```

---

## 4. Dockerfile 说明

```
python:3.11-slim         基础镜像（100MB，比完整镜像小 10 倍）
  ↓
COPY uv                  安装 uv 包管理器
  ↓
COPY pyproject.toml      先复制依赖文件（Docker 层缓存，代码改了依赖不动就不重建这层）
  ↓
uv sync --frozen         安装依赖（锁定版本）
  ↓
COPY src/                复制源代码
  ↓
EXPOSE 8000              声明端口
  ↓
CMD uv run run           启动（pyproject.toml 中 run = "app.main:run"）
```

---

## 5. 生产 vs 开发环境

| | 开发（start） | 生产（run） |
|---|---|---|
| 入口函数 | `app.main:start` | `app.main:run` |
| reload | `True`（自动重启） | 否 |
| workers | 1 | 4 |
| host | 默认 127.0.0.1 | `0.0.0.0`（所有网卡） |
| 端口清理 | 启动前 kill 8000 | 不需要 |

---

## 6. 常用运维命令

```bash
docker logs --tail=50 web-fastapi     # 最近 50 行日志
docker restart web-fastapi            # 重启
docker stop web-fastapi && docker rm web-fastapi  # 停止并删除
docker exec -it web-fastapi /bin/bash  # 进入容器调试
```
