#!/bin/bash
# Graphiti MCP Server Neo4j 快速部署脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_SERVER_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$MCP_SERVER_DIR/.." && pwd)"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Graphiti MCP Server - Neo4j 部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 步骤 1: 检查前置条件
echo -e "${YELLOW}[1/5] 检查前置条件...${NC}"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    exit 1
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: Docker Compose 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker 和 Docker Compose 已安装${NC}"

# 步骤 2: 检查 .env 文件
echo -e "${YELLOW}[2/5] 检查环境配置...${NC}"

ENV_FILE="$MCP_SERVER_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}未找到 .env 文件，正在创建模板...${NC}"
    cat > "$ENV_FILE" << 'EOF'
# OpenAI API Key (必需)
OPENAI_API_KEY=your_openai_api_key_here

# Neo4j 配置
NEO4J_USER=neo4j
NEO4J_PASSWORD=demodemo
NEO4J_DATABASE=neo4j

# LLM 配置
MODEL_NAME=gpt-4.1-mini
SMALL_MODEL_NAME=gpt-4.1-nano
EMBEDDER_MODEL_NAME=text-embedding-3-small
LLM_TEMPERATURE=0.0

# Graphiti 配置
GRAPHITI_GROUP_ID=main
SEMAPHORE_LIMIT=10

# Neo4j 并行运行时（Enterprise）
USE_PARALLEL_RUNTIME=false
EOF
    echo -e "${YELLOW}已创建 .env 文件模板，请编辑 $ENV_FILE 并设置你的 API Key${NC}"
    echo -e "${RED}请先编辑 .env 文件，然后重新运行此脚本${NC}"
    exit 1
fi

# 检查 API Key
if grep -q "your_openai_api_key_here" "$ENV_FILE"; then
    echo -e "${RED}错误: 请在 .env 文件中设置你的 OPENAI_API_KEY${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 环境配置文件已就绪${NC}"

# 步骤 3: 构建 Docker 镜像
echo -e "${YELLOW}[3/5] 构建 Docker 镜像...${NC}"

cd "$SCRIPT_DIR"

if [ -f "build-standalone.sh" ]; then
    chmod +x build-standalone.sh
    echo "使用构建脚本构建镜像..."
    ./build-standalone.sh
else
    echo "手动构建镜像..."
    MCP_VERSION=$(grep '^version = ' "$MCP_SERVER_DIR/pyproject.toml" | sed 's/version = "\(.*\)"/\1/')
    GRAPHITI_CORE_VERSION=$(curl -s https://pypi.org/pypi/graphiti-core/json | python3 -c "import sys, json; print(json.load(sys.stdin)['info']['version'])")
    BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    VCS_REF=$(git -C "$PROJECT_ROOT" rev-parse --short HEAD 2>/dev/null || echo "unknown")
    
    docker build \
      --build-arg MCP_SERVER_VERSION="${MCP_VERSION}" \
      --build-arg GRAPHITI_CORE_VERSION="${GRAPHITI_CORE_VERSION}" \
      --build-arg BUILD_DATE="${BUILD_DATE}" \
      --build-arg VCS_REF="${VCS_REF}" \
      -f Dockerfile.standalone \
      -t graphiti-mcp-neo4j:latest \
      "$MCP_SERVER_DIR"
fi

echo -e "${GREEN}✓ Docker 镜像构建完成${NC}"

# 步骤 4: 启动服务
echo -e "${YELLOW}[4/5] 启动服务...${NC}"

cd "$MCP_SERVER_DIR"

# 停止可能存在的旧服务
docker compose -f docker/docker-compose-neo4j.yml down 2>/dev/null || true

# 启动服务
docker compose -f docker/docker-compose-neo4j.yml up -d

echo -e "${GREEN}✓ 服务已启动${NC}"

# 步骤 5: 等待服务就绪
echo -e "${YELLOW}[5/5] 等待服务就绪...${NC}"

echo "等待 Neo4j 启动（最多 60 秒）..."
for i in {1..60}; do
    if docker compose -f docker/docker-compose-neo4j.yml exec -T neo4j wget -qO- http://localhost:7474 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Neo4j 已就绪${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${RED}警告: Neo4j 启动超时，但继续检查 MCP 服务器...${NC}"
    fi
    sleep 1
done

echo "等待 MCP 服务器启动（最多 30 秒）..."
for i in {1..30}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ MCP 服务器已就绪${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}警告: MCP 服务器启动超时${NC}"
    fi
    sleep 1
done

# 显示服务状态
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "服务信息："
echo "  - MCP 服务器: http://localhost:8000"
echo "  - MCP 端点:   http://localhost:8000/mcp/"
echo "  - 健康检查:   http://localhost:8000/health"
echo "  - Neo4j 浏览器: http://localhost:7474"
echo "  - Neo4j Bolt:   bolt://localhost:7687"
echo ""
echo "常用命令："
echo "  查看日志:   docker compose -f docker/docker-compose-neo4j.yml logs -f"
echo "  停止服务:   docker compose -f docker/docker-compose-neo4j.yml down"
echo "  重启服务:   docker compose -f docker/docker-compose-neo4j.yml restart"
echo ""
echo "查看详细部署文档: docker/DEPLOY_NEO4J.md"

