# Neo4j 快速部署指南

## 一键部署（推荐）

```bash
cd /home/ubuntu/project/graphiti/mcp_server
./docker/deploy-neo4j.sh
```

## 手动部署步骤

### 1. 创建环境变量文件

```bash
cd /home/ubuntu/project/graphiti/mcp_server
cat > .env << 'EOF'
OPENAI_API_KEY=your_api_key_here
NEO4J_PASSWORD=your_secure_password
EOF
```

### 2. 构建镜像

```bash
cd docker
./build-standalone.sh
```

### 3. 启动服务

```bash
cd ..
docker compose -f docker/docker-compose-neo4j.yml up -d
```

### 4. 验证部署

```bash
# 检查健康状态
curl http://localhost:8000/health

# 查看日志
docker compose -f docker/docker-compose-neo4j.yml logs -f
```

## 常用命令

```bash
# 启动服务
docker compose -f docker/docker-compose-neo4j.yml up -d

# 停止服务
docker compose -f docker/docker-compose-neo4j.yml down

# 查看日志
docker compose -f docker/docker-compose-neo4j.yml logs -f

# 重启服务
docker compose -f docker/docker-compose-neo4j.yml restart

# 查看状态
docker compose -f docker/docker-compose-neo4j.yml ps
```

## 服务地址

- **MCP 服务器**: http://localhost:8000
- **MCP 端点**: http://localhost:8000/mcp/
- **Neo4j 浏览器**: http://localhost:7474
- **Neo4j Bolt**: bolt://localhost:7687

## 配置 MCP 客户端

### Cursor IDE

编辑 `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "graphiti-memory": {
      "url": "http://localhost:8000/mcp/"
    }
  }
}
```

## 故障排查

```bash
# 检查容器状态
docker compose -f docker/docker-compose-neo4j.yml ps

# 查看详细日志
docker compose -f docker/docker-compose-neo4j.yml logs graphiti-mcp
docker compose -f docker/docker-compose-neo4j.yml logs neo4j

# 检查端口占用
lsof -i :8000
lsof -i :7474
lsof -i :7687
```

## 详细文档

查看完整部署文档: [DEPLOY_NEO4J.md](./DEPLOY_NEO4J.md)

