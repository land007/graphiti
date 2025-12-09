# Neo4j Docker 部署指南

本指南将帮助你构建和部署使用 Neo4j 的 Graphiti MCP 服务器。

## 前置要求

1. Docker 和 Docker Compose 已安装
2. OpenAI API Key（或其他 LLM 提供商的 API Key）
3. 足够的系统资源：
   - 至少 2GB 可用内存
   - 至少 10GB 可用磁盘空间

## 步骤 1: 准备环境变量

在 `mcp_server` 目录下创建 `.env` 文件：

```bash
cd /home/ubuntu/project/graphiti/mcp_server
cat > .env << 'EOF'
# 必需：OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Neo4j 配置（可选，有默认值）
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password_here
NEO4J_DATABASE=neo4j

# LLM 配置（可选）
MODEL_NAME=gpt-4.1-mini
SMALL_MODEL_NAME=gpt-4.1-nano
EMBEDDER_MODEL_NAME=text-embedding-3-small
LLM_TEMPERATURE=0.0

# Graphiti 配置（可选）
GRAPHITI_GROUP_ID=main
SEMAPHORE_LIMIT=10

# 可选：Neo4j 并行运行时（Enterprise 版本）
USE_PARALLEL_RUNTIME=false
EOF
```

**重要提示：**
- 将 `your_openai_api_key_here` 替换为你的实际 OpenAI API Key
- 将 `your_secure_password_here` 替换为强密码
- 确保 `.env` 文件不会被提交到 Git（已在 .gitignore 中）

## 步骤 2: 构建 Docker 镜像

### 方式 1: 使用构建脚本（推荐）

```bash
cd /home/ubuntu/project/graphiti/mcp_server/docker
chmod +x build-standalone.sh
./build-standalone.sh
```

这个脚本会：
- 自动从 PyPI 获取最新的 `graphiti-core` 版本
- 构建包含 Neo4j 和 FalkorDB 支持的镜像
- 创建多个标签便于版本管理

### 方式 2: 手动构建

```bash
cd /home/ubuntu/project/graphiti/mcp_server/docker

# 获取版本信息
MCP_VERSION=$(grep '^version = ' ../pyproject.toml | sed 's/version = "\(.*\)"/\1/')
GRAPHITI_CORE_VERSION=$(curl -s https://pypi.org/pypi/graphiti-core/json | python3 -c "import sys, json; print(json.load(sys.stdin)['info']['version'])")
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# 构建镜像
docker build \
  --build-arg MCP_SERVER_VERSION="${MCP_VERSION}" \
  --build-arg GRAPHITI_CORE_VERSION="${GRAPHITI_CORE_VERSION}" \
  --build-arg BUILD_DATE="${BUILD_DATE}" \
  --build-arg VCS_REF="${VCS_REF}" \
  -f Dockerfile.standalone \
  -t graphiti-mcp-neo4j:latest \
  -t graphiti-mcp-neo4j:${MCP_VERSION} \
  ..
```

## 步骤 3: 使用 Docker Compose 部署

### 启动服务

```bash
cd /home/ubuntu/project/graphiti/mcp_server
docker compose -f docker/docker-compose-neo4j.yml up -d
```

### 查看日志

```bash
# 查看所有服务日志
docker compose -f docker/docker-compose-neo4j.yml logs -f

# 只查看 MCP 服务器日志
docker compose -f docker/docker-compose-neo4j.yml logs -f graphiti-mcp

# 只查看 Neo4j 日志
docker compose -f docker/docker-compose-neo4j.yml logs -f neo4j
```

### 检查服务状态

```bash
# 检查容器状态
docker compose -f docker/docker-compose-neo4j.yml ps

# 检查健康状态
curl http://localhost:8000/health

# 访问 Neo4j 浏览器（需要先设置密码）
# 浏览器打开: http://localhost:7474
```

## 步骤 4: 验证部署

### 测试 MCP 服务器

```bash
# 健康检查
curl http://localhost:8000/health

# 测试 MCP 端点
curl http://localhost:8000/mcp/
```

### 测试 Neo4j 连接

```bash
# 使用 cypher-shell 连接（在容器内）
docker compose -f docker/docker-compose-neo4j.yml exec neo4j cypher-shell -u neo4j -p your_password

# 在 cypher-shell 中运行：
# MATCH (n) RETURN count(n) LIMIT 1;
```

## 步骤 5: 配置 MCP 客户端

### Cursor IDE 配置

编辑 Cursor 的 MCP 配置文件（通常在 `~/.cursor/mcp.json` 或项目配置中）：

```json
{
  "mcpServers": {
    "graphiti-memory": {
      "url": "http://localhost:8000/mcp/"
    }
  }
}
```

### VS Code / GitHub Copilot 配置

在 VS Code 设置中添加：

```json
{
  "mcpServers": {
    "graphiti": {
      "uri": "http://localhost:8000/mcp/",
      "transport": {
        "type": "http"
      }
    }
  }
}
```

## 常用操作命令

### 停止服务

```bash
docker compose -f docker/docker-compose-neo4j.yml down
```

### 停止并删除数据（谨慎使用）

```bash
docker compose -f docker/docker-compose-neo4j.yml down -v
```

### 重启服务

```bash
docker compose -f docker/docker-compose-neo4j.yml restart
```

### 更新镜像并重启

```bash
# 重新构建镜像
cd /home/ubuntu/project/graphiti/mcp_server/docker
./build-standalone.sh

# 重启服务
cd ..
docker compose -f docker/docker-compose-neo4j.yml up -d --force-recreate
```

## 数据管理

### 备份 Neo4j 数据

```bash
# 备份数据卷
docker run --rm \
  -v mcp_server_neo4j_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/neo4j-data-backup-$(date +%Y%m%d).tar.gz -C /data .

# 备份日志
docker run --rm \
  -v mcp_server_neo4j_logs:/logs \
  -v $(pwd):/backup \
  alpine tar czf /backup/neo4j-logs-backup-$(date +%Y%m%d).tar.gz -C /logs .
```

### 恢复 Neo4j 数据

```bash
# 停止服务
docker compose -f docker/docker-compose-neo4j.yml down

# 恢复数据
docker run --rm \
  -v mcp_server_neo4j_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/neo4j-data-backup-YYYYMMDD.tar.gz -C /data

# 启动服务
docker compose -f docker/docker-compose-neo4j.yml up -d
```

## 性能优化

### 调整 Neo4j 内存设置

编辑 `docker/docker-compose-neo4j.yml`，修改环境变量：

```yaml
environment:
  - NEO4J_server_memory_heap_initial__size=1G  # 初始堆内存
  - NEO4J_server_memory_heap_max__size=2G      # 最大堆内存
  - NEO4J_server_memory_pagecache_size=1G      # 页面缓存大小
```

### 调整并发限制

在 `.env` 文件中调整：

```bash
# 根据你的 LLM 提供商配额调整
SEMAPHORE_LIMIT=15  # OpenAI Tier 3: 10-15, Tier 4: 20-50
```

### 启用并行运行时（Enterprise 版本）

```bash
# 在 .env 文件中设置
USE_PARALLEL_RUNTIME=true
```

## 故障排查

### 检查容器状态

```bash
docker compose -f docker/docker-compose-neo4j.yml ps
```

### 查看详细日志

```bash
# MCP 服务器日志
docker compose -f docker/docker-compose-neo4j.yml logs graphiti-mcp

# Neo4j 日志
docker compose -f docker/docker-compose-neo4j.yml logs neo4j
```

### 检查端口占用

```bash
# 检查端口 8000（MCP 服务器）
lsof -i :8000

# 检查端口 7474（Neo4j HTTP）
lsof -i :7474

# 检查端口 7687（Neo4j Bolt）
lsof -i :7687
```

### 重置 Neo4j 密码

如果忘记了 Neo4j 密码：

```bash
# 停止服务
docker compose -f docker/docker-compose-neo4j.yml down

# 删除认证数据
docker volume rm mcp_server_neo4j_data

# 重新启动（会创建新的默认密码）
docker compose -f docker/docker-compose-neo4j.yml up -d
```

### 常见错误

1. **连接超时**
   - 确保 Neo4j 健康检查通过（等待 30 秒）
   - 检查防火墙设置

2. **API Key 错误**
   - 验证 `.env` 文件中的 `OPENAI_API_KEY` 是否正确
   - 检查环境变量是否被正确加载

3. **内存不足**
   - 增加 Docker 内存限制
   - 减少 Neo4j 堆内存设置

## 生产环境建议

1. **使用强密码**：修改默认的 Neo4j 密码
2. **启用 HTTPS**：在生产环境中使用反向代理（如 Nginx）
3. **定期备份**：设置自动备份脚本
4. **监控资源**：使用 Docker stats 或监控工具
5. **日志管理**：配置日志轮转和集中日志管理

## 下一步

- 查看 [MCP 服务器 README](../README.md) 了解功能
- 查看 [Cursor 规则文档](../docs/cursor_rules.md) 配置 AI 助手
- 查看 [测试文档](../tests/README.md) 了解如何测试

