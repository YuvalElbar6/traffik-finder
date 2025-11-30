# 🚀 Wazuh MCP Security Assistant - Docker Deployment

Complete cross-platform Docker deployment for the Wazuh MCP Security Assistant with separate containers for server and client.

## 📋 Table of Contents

- [Architecture Overview](#-architecture-overview)
- [Prerequisites](#-prerequisites)
- [File Structure](#-file-structure)
- [Quick Start](#-quick-start)
- [Environment Configuration](#-environment-configuration)
- [Building Images](#-building-images)
- [Running Services](#-running-services)
- [Cross-Platform Support](#-cross-platform-support)
- [Usage Examples](#-usage-examples)
- [Troubleshooting](#-troubleshooting)
- [Maintenance](#-maintenance)

## 🏗️ Architecture Overview

### Two-Container Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Environment                      │
│                                                              │
│  ┌────────────────────┐         ┌──────────────────────┐   │
│  │    MCP Server      │         │   Wazuh Client       │   │
│  │   (Port 8080)      │ ◄─────► │  (Interactive CLI)   │   │
│  │                    │  HTTP   │                      │   │
│  │ Dockerfile.server  │         │  Dockerfile.client   │   │
│  └────────────────────┘         └──────────────────────┘   │
│           │                              │                  │
│           │                              │                  │
│           └──────────┬───────────────────┘                  │
│                      │                                      │
│                ┌─────▼──────┐                              │
│                │  ChromaDB  │                              │
│                │(Shared Vol)│                              │
│                └────────────┘                              │
│                      │                                      │
│                ┌─────▼──────┐                              │
│                │  .env file │                              │
│                │ (Mounted)  │                              │
│                └────────────┘                              │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │   Wazuh API    │
              │ Wazuh Indexer  │
              └────────────────┘
```

### Why Two Dockerfiles?

**Dockerfile.server** - MCP Server
- Lightweight (~400MB)
- Only includes server components
- Runs MCP protocol server
- Provides Wazuh API tools

**Dockerfile.client** - Wazuh Client
- Full application (~550MB)
- Includes AI agent
- Interactive CLI interface
- GPT-4 integration

### Environment Variable Handling

The `.env` file is handled in two ways for maximum flexibility:

**Primary Method**: `env_file` directive in `docker-compose.yml`
- Automatically loads variables into container environment
- No code changes needed
- Standard Docker Compose pattern

**Backup Method**: Volume mount at `/app/.env`
- File is mounted read-only
- Python code can use `python-dotenv`
- Fallback if `env_file` fails

## 📦 Prerequisites

### Required Software

- **Docker**: 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: 2.0+ ([Install Compose](https://docs.docker.com/compose/install/))

### Supported Platforms

✅ Linux (amd64, arm64)  
✅ macOS (Intel, Apple Silicon)  
✅ Windows (WSL2, Docker Desktop)

### Required Access

- Wazuh Manager API
- Wazuh Indexer (OpenSearch)
- OpenAI API key

## 📁 File Structure

```
wazuh-mcp-docker/
├── .env                    # Your configuration (REQUIRED)
├── .env.example           # Template for .env
├── docker-compose.yml     # Orchestration config
│
├── Dockerfile.server      # MCP server image
├── Dockerfile.client      # Wazuh client image
│
├── Python Application Files/
│   ├── mcp_server.py          # MCP server (server only)
│   ├── mcp_helper.py          # MCP utilities (server only)
│   ├── mcp_client_call.py     # API client (both)
│   ├── wazuh_client.py        # Interactive client (client only)
│   ├── agent_prompt.py        # AI prompts (client only)
│   ├── chroma_run.py          # ChromaDB workflow (client only)
│   ├── rag_*.py               # RAG components (client only)
│   └── requirements.txt       # Python dependencies (both)
│
└── Data Directories/
    └── rag_chroma/            # ChromaDB persistent storage (shared)
```

## 🚀 Quick Start

### Step 1: Prepare Environment

```bash
# Clone or download your project
cd wazuh-mcp-docker

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

### Step 2: Configure .env File

```bash
# Wazuh Configuration
WAZUH_API_URL=https://your-wazuh-manager:55000
WAZUH_API_USER=your-username
WAZUH_API_PASSWORD=your-password

# Wazuh Indexer Configuration
WAZUH_INDEXER_URL=https://your-indexer:9200
WAZUH_INDEXER_USER=admin
WAZUH_INDEXER_PASSWORD=your-indexer-password

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4

# MCP Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8080
```

### Step 3: Build and Run

```bash
# Build both images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

### Step 4: Use the Client

```bash
# Interactive mode
docker-compose run --rm wazuh-client

# One-off query
docker-compose run --rm wazuh-client --query "Show me critical vulnerabilities"
```

## ⚙️ Environment Configuration

### Complete .env Template

```bash
# ============================================
# Wazuh API Configuration
# ============================================
WAZUH_API_URL=https://wazuh-manager.example.com:55000
WAZUH_API_USER=wazuh-wui
WAZUH_API_PASSWORD=SecurePassword123!

# ============================================
# Wazuh Indexer (OpenSearch) Configuration
# ============================================
WAZUH_INDEXER_URL=https://wazuh-indexer.example.com:9200
WAZUH_INDEXER_USER=admin
WAZUH_INDEXER_PASSWORD=IndexerPassword123!

# ============================================
# OpenAI Configuration
# ============================================
OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz123456789
OPENAI_MODEL=gpt-4  # or gpt-4-turbo, gpt-3.5-turbo

# ============================================
# MCP Server Configuration
# ============================================
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8080

# ============================================
# ChromaDB Configuration
# ============================================
CHROMA_PERSIST_DIRECTORY=/app/rag_chroma
CHROMA_COLLECTION_NAME=wazuh_rules

# ============================================
# Logging Configuration
# ============================================
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

## 🔨 Building Images

### Build All Images

```bash
docker-compose build
```

### Build Specific Service

```bash
# Build only MCP server
docker-compose build mcp-server

# Build only Wazuh client
docker-compose build wazuh-client
```

### Build with No Cache

```bash
docker-compose build --no-cache
```

### Build for Specific Platform

```bash
# For ARM64 (Apple Silicon, ARM servers)
docker-compose build --build-arg BUILDPLATFORM=linux/arm64

# For AMD64 (Intel/AMD)
docker-compose build --build-arg BUILDPLATFORM=linux/amd64
```

## 🏃 Running Services

### Start All Services

```bash
# Detached mode (background)
docker-compose up -d

# Foreground mode (see logs)
docker-compose up
```

### Start Specific Service

```bash
docker-compose up -d mcp-server
```

### Run Interactive Client

```bash
# Interactive shell
docker-compose run --rm wazuh-client

# With specific query
docker-compose run --rm wazuh-client --query "List all active agents"

# With debugging
docker-compose run --rm wazuh-client --debug
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f mcp-server
docker-compose logs -f wazuh-client

# Last 100 lines
docker-compose logs --tail=100 mcp-server
```

### Stop Services

```bash
# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop mcp-server
```

## 🌍 Cross-Platform Support

### Linux

```bash
# Standard Docker installation
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Run without sudo (optional)
sudo usermod -aG docker $USER
newgrp docker
```

### macOS

```bash
# Install Docker Desktop
brew install --cask docker

# Or download from:
# https://www.docker.com/products/docker-desktop

# Start Docker Desktop and run:
docker-compose up -d
```

### Windows (WSL2)

```powershell
# 1. Install WSL2
wsl --install

# 2. Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop

# 3. Enable WSL2 backend in Docker Desktop settings

# 4. In WSL2 terminal:
cd /path/to/wazuh-mcp-docker
docker-compose up -d
```

### Platform-Specific Notes

**Apple Silicon (M1/M2/M3)**
```bash
# Images are multi-arch compatible
# No special configuration needed
docker-compose up -d
```

**Raspberry Pi (ARM)**
```bash
# Use arm64 builds
docker-compose build --build-arg BUILDPLATFORM=linux/arm64
docker-compose up -d
```

## 💡 Usage Examples

### Example 1: Query Agent Information

```bash
docker-compose run --rm wazuh-client --query "Show me all disconnected agents"
```

### Example 2: Check Critical Vulnerabilities

```bash
docker-compose run --rm wazuh-client --query "What are the critical vulnerabilities on agent 001?"
```

### Example 3: Interactive Session

```bash
docker-compose run --rm wazuh-client

# Inside the container:
> Show me the cluster health status
> List all security alerts from the last hour
> What are the top 10 rules triggered today?
> exit
```

### Example 4: Custom ChromaDB Query

```bash
docker-compose run --rm wazuh-client --query "Find rules related to SSH authentication failures"
```

### Example 5: Export Data

```bash
# Run client with volume mount for exports
docker-compose run --rm -v $(pwd)/exports:/exports wazuh-client \
  --query "Export all agent data to CSV" --output /exports/agents.csv
```

## 🔧 Troubleshooting

### Common Issues

#### 1. MCP Server Not Responding

```bash
# Check if server is running
docker-compose ps

# View server logs
docker-compose logs mcp-server

# Restart server
docker-compose restart mcp-server
```

#### 2. Client Can't Connect to Server

```bash
# Check network connectivity
docker-compose exec wazuh-client ping mcp-server

# Verify port mapping
docker-compose port mcp-server 8080

# Check environment variables
docker-compose exec wazuh-client env | grep MCP
```

#### 3. Wazuh API Connection Failed

```bash
# Verify credentials in .env
cat .env | grep WAZUH_API

# Test API connection manually
docker-compose run --rm wazuh-client python -c "
from mcp_client_call import test_wazuh_connection
test_wazuh_connection()
"
```

#### 4. ChromaDB Persistence Issues

```bash
# Check volume exists
docker volume ls | grep rag_chroma

# Inspect volume
docker volume inspect wazuh-mcp-docker_rag_chroma

# Rebuild ChromaDB
docker-compose run --rm wazuh-client python chroma_run.py
```

#### 5. Permission Denied Errors

```bash
# Fix ChromaDB directory permissions
sudo chown -R 1000:1000 rag_chroma/

# Or run with user override
docker-compose run --user root --rm wazuh-client bash
```

### Debug Mode

```bash
# Enable debug logging
docker-compose run --rm -e LOG_LEVEL=DEBUG wazuh-client

# Run with shell access
docker-compose run --rm wazuh-client bash

# Inside container, manually run scripts
python wazuh_client.py --debug
```

### Network Troubleshooting

```bash
# Inspect Docker network
docker network inspect wazuh-mcp-docker_default

# Test external connectivity
docker-compose run --rm wazuh-client curl -k $WAZUH_API_URL

# Check DNS resolution
docker-compose run --rm wazuh-client nslookup wazuh-manager
```

## 🛠️ Maintenance

### Update Images

```bash
# Pull latest base images
docker-compose pull

# Rebuild with latest code
docker-compose build --no-cache

# Restart services
docker-compose up -d --force-recreate
```

### Backup ChromaDB Data

```bash
# Create backup
docker run --rm -v wazuh-mcp-docker_rag_chroma:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/chromadb-backup-$(date +%Y%m%d).tar.gz /data

# Restore backup
docker run --rm -v wazuh-mcp-docker_rag_chroma:/data -v $(pwd):/backup \
  ubuntu tar xzf /backup/chromadb-backup-20240101.tar.gz -C /
```

### Clean Up

```bash
# Remove stopped containers
docker-compose rm

# Remove unused images
docker image prune -a

# Remove all project resources
docker-compose down -v --rmi all

# Complete Docker cleanup
docker system prune -a --volumes
```

### Monitor Resource Usage

```bash
# Check container stats
docker stats

# Check disk usage
docker system df

# Check specific service resources
docker-compose exec mcp-server top
```

### Update Dependencies

```bash
# Update Python packages
docker-compose run --rm wazuh-client pip list --outdated

# Rebuild after requirements.txt changes
docker-compose build --no-cache wazuh-client
```

## 📊 Health Checks

### Automated Health Monitoring

```bash
# Check service health
docker-compose ps

# MCP Server health endpoint
curl http://localhost:8080/health

# View health check logs
docker inspect --format='{{json .State.Health}}' wazuh-mcp-docker-mcp-server-1 | jq
```

### Manual Health Verification

```bash
# Test MCP server
docker-compose exec mcp-server python -c "
import requests
response = requests.get('http://localhost:8080/health')
print(response.json())
"

# Test Wazuh connectivity
docker-compose run --rm wazuh-client python -c "
from mcp_client_call import MCPClient
client = MCPClient()
print(client.get_agents())
"
```

## 📝 Development Tips

### Local Development

```bash
# Mount local code for development
docker-compose run --rm -v $(pwd):/app wazuh-client bash

# Live reload (modify docker-compose.yml to add volume mounts)
volumes:
  - .:/app
  - /app/rag_chroma
```

### Testing Changes

```bash
# Run tests inside container
docker-compose run --rm wazuh-client pytest

# Run specific test file
docker-compose run --rm wazuh-client python -m pytest tests/test_client.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test with Docker (`docker-compose build && docker-compose up`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Resources

- [Wazuh Documentation](https://documentation.wazuh.com/)
- [Docker Documentation](https://docs.docker.com/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## 💬 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**Made with ❤️ for Wazuh Security Operations**
