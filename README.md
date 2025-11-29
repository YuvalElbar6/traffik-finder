🚀 Wazuh MCP Security Assistant - Docker Deployment
Complete cross-platform Docker deployment for the Wazuh MCP Security Assistant with separate containers for server and client.
📋 Table of Contents

Architecture Overview
Prerequisites
File Structure
Quick Start
Environment Configuration
Building Images
Running Services
Cross-Platform Support
Usage Examples
Troubleshooting
Maintenance

🏗️ Architecture Overview
Two-Container Architecture
┌─────────────────────────────────────────────────────────────┐
│                    Docker Environment                        │
│                                                              │
│  ┌────────────────────┐         ┌──────────────────────┐   │
│  │  MCP Server        │         │  Wazuh Client        │   │
│  │  (Port 8080)       │ ◄─────► │  (Interactive CLI)   │   │
│  │                    │  HTTP   │                      │   │
│  │  Dockerfile.server │         │  Dockerfile.client   │   │
│  └────────────────────┘         └──────────────────────┘   │
│           │                              │                  │
│           └──────────┬───────────────────┘                  │
│                      │                                      │
│              ┌───────▼────────┐                            │
│              │  ChromaDB      │                            │
│              │  (Shared Vol)  │                            │
│              └────────────────┘                            │
│                      │                                      │
│              ┌───────▼────────┐                            │
│              │  .env file     │                            │
│              │  (Mounted)     │                            │
│              └────────────────┘                            │
└─────────────────────────────────────────────────────────────┘
        │                    │
        ▼                    ▼
   Wazuh API          Wazuh Indexer
Why Two Dockerfiles?

Dockerfile.server - MCP Server

Lightweight (~400MB)
Only includes server components
Runs MCP protocol server
Provides Wazuh API tools


Dockerfile.client - Wazuh Client

Full application (~550MB)
Includes AI agent
Interactive CLI interface
GPT-4 integration



Environment Variable Handling
The .env file is handled in two ways for maximum flexibility:

Primary Method: env_file directive in docker-compose.yml

Automatically loads variables into container environment
No code changes needed
Standard Docker Compose pattern


Backup Method: Volume mount at /app/.env

File is mounted read-only
Python code can use python-dotenv
Fallback if env_file fails



📦 Prerequisites
Required Software

Docker: 20.10+ (Install Docker)
Docker Compose: 2.0+ (Install Compose)

Supported Platforms
✅ Linux (amd64, arm64)
✅ macOS (Intel, Apple Silicon)
✅ Windows (WSL2, Docker Desktop)
Required Access

Wazuh Manager API
Wazuh Indexer (OpenSearch)
OpenAI API key

📁 File Structure
wazuh-mcp-docker/
├── .env                        # Your configuration (REQUIRED)
├── .env.example               # Template for .env
├── docker-compose.yml         # Orchestration config
│
├── Dockerfile.server      # MCP server image
├── Dockerfile.client      # Wazuh client image
│
├── Python Application Files/
│   ├── mcp_server.py         # MCP server (server only)
│   ├── mcp_helper.py         # MCP utilities (server only)
│   ├── mcp_client_call.py    # API client (both)
│   ├── wazuh_client.py       # Interactive client (client only)
│   ├── agent_prompt.py       # AI prompts (client only)
│   ├── chroma_run.py         # ChromaDB workflow (client only)
│   ├── rag_*.py              # RAG components (client only)
│   └── requirements.txt      # Python dependencies (both)
│
└── Data Directories/
    └── rag_chroma/           # ChromaDB persistent storage (shared)
🚀 Quick Start
Step 1: Prepare Environment
bash# Clone or download your project
cd wazuh-mcp-docker

# Copy the .env file from your project
cp /path/to/your/_env .env

# OR create from template
cp .env.example .env
nano .env  # Edit with your credentials
Step 2: Build Images
bash# Build both images
docker-compose build

# Or build individually
docker-compose build wazuh-mcp-server
docker-compose build wazuh-client
Step 3: Start Services
bash# Start both services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
Step 4: Use the Client
bash# Attach to interactive client
docker attach wazuh-client

# OR run client in new container
docker-compose run --rm wazuh-client
⚙️ Environment Configuration
Your .env File Location
The .env file must be in the same directory as docker-compose.yml:
wazuh-mcp-docker/
├── .env                    ← Put your _env file here (rename to .env)
├── docker-compose.yml
└── ...
.env File Format
Your existing _env file should be renamed to .env:
bash# Wazuh Server Configuration
WAZUH_API="https://127.0.0.1:55000"
WAZUH_USER="w<WAZUH_USER>"
WAZUH_PASSWORD=""

# Wazuh Indexer Configuration
WAZUH_INDEXER_API="https://127.0.0.1:9200"
WAZUH_INDEXER_USER="<WAZUH_ADMIN>"
WAZUH_INDEXER_PASSWORD=""

# OpenAI API Key
api_key=""
How Environment Variables Work
Docker Compose loads .env in two ways:

As environment variables (via env_file: - .env)

python   import os
   wazuh_api = os.getenv('WAZUH_API')

As mounted file (via volumes)

python   from dotenv import load_dotenv
   load_dotenv('/app/.env')  # Fallback method
🔨 Building Images
Standard Build
bash# Build all images
docker-compose build

# Build with no cache
docker-compose build --no-cache

# Build specific service
docker-compose build wazuh-mcp-server
Cross-Platform Build
bash# Build for specific platform
docker-compose build --platform linux/amd64

# Build for multiple platforms (requires buildx)
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -f Dockerfile.server -t wazuh-mcp-server:latest .
Build Options
bash# Parallel build (faster)
docker-compose build --parallel

# Pull latest base images first
docker-compose build --pull

# Quiet mode
docker-compose build --quiet
▶️ Running Services
Start Services
bash# Start in background (detached)
docker-compose up -d

# Start and view logs
docker-compose up

# Start specific service
docker-compose up -d wazuh-mcp-server
Stop Services
bash# Stop all services
docker-compose down

# Stop but keep volumes
docker-compose stop

# Stop specific service
docker-compose stop wazuh-client
Restart Services
bash# Restart all
docker-compose restart

# Restart specific service
docker-compose restart wazuh-mcp-server
🌍 Cross-Platform Support
Platform Detection
The Dockerfiles automatically detect and build for the correct platform:
dockerfileFROM --platform=$BUILDPLATFORM python:3.11-slim
Supported platforms:

linux/amd64 - Intel/AMD 64-bit
linux/arm64 - ARM 64-bit (Apple Silicon, ARM servers)

Building for Specific Platform
bash# For Intel/AMD (most common)
docker-compose build --platform linux/amd64

# For ARM (Apple Silicon Mac, ARM servers)
docker-compose build --platform linux/arm64

# For current platform (automatic)
docker-compose build
Testing on Different Platforms
bash# On Mac M1/M2 (ARM)
docker-compose build  # Builds for arm64 automatically

# On Intel Mac or Linux
docker-compose build  # Builds for amd64 automatically

# On Windows with WSL2
docker-compose build  # Builds for amd64 automatically
Multi-Architecture Images
To build for multiple platforms:
bash# Setup buildx (one-time)
docker buildx create --name multiplatform --use
docker buildx inspect --bootstrap

# Build for both platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f Dockerfile.server \
  -t wazuh-mcp-server:latest \
  --push .
💻 Usage Examples
Server Only Mode
Run just the MCP server:
bash# Start server
docker-compose up -d wazuh-mcp-server

# Test server
curl http://localhost:8080/

# View logs
docker-compose logs -f wazuh-mcp-server
Client Only Mode
Run client connecting to existing server:
bash# Ensure server is running first
docker-compose up -d wazuh-mcp-server

# Run interactive client
docker-compose run --rm wazuh-client

# Or attach to running client
docker attach wazuh-client
Full Stack Mode
Run both server and client:
bash# Start everything
docker-compose up -d

# Attach to client
docker attach wazuh-client

# Detach without stopping: Ctrl+P, Ctrl+Q
Development Mode
Run with code changes:
bash# Mount source code as volumes (add to docker-compose.yml)
volumes:
  - ./mcp_server.py:/app/mcp_server.py
  - ./wazuh_client.py:/app/wazuh_client.py

# Restart to apply changes
docker-compose restart
🔧 Troubleshooting
.env File Not Found
bash# Error: .env: no such file or directory
# Solution: Copy your _env file
cp _env .env

# Verify file exists
ls -la .env
Permission Denied
bash# Error: permission denied
# Solution: Fix permissions
chmod 644 .env
chmod +x start.sh
Port Already in Use
bash# Error: port 8080 already allocated
# Solution 1: Stop conflicting service
docker ps
docker stop <container-id>

# Solution 2: Change port in docker-compose.yml
ports:
  - "8081:8080"  # Use 8081 instead
Container Won't Start
bash# Check logs
docker-compose logs wazuh-mcp-server

# Check container status
docker-compose ps

# Inspect container
docker inspect wazuh-mcp-server
Environment Variables Not Loading
bash# Verify .env file
cat .env

# Check loaded variables
docker-compose config

# Test inside container
docker-compose exec wazuh-mcp-server env | grep WAZUH
Connection to Wazuh Failed
bash# Test from container
docker-compose exec wazuh-mcp-server curl -k https://54.172.121.51:55000

# Check network
docker network inspect wazuh-network

# Verify credentials
docker-compose exec wazuh-mcp-server python -c "from mcp_client_call import get_token; print(get_token())"
Cross-Platform Issues
bash# Check platform
docker-compose exec wazuh-mcp-server uname -m
# x86_64 = amd64
# aarch64 = arm64

# Rebuild for correct platform
docker-compose build --no-cache --platform linux/$(uname -m)
🛠️ Maintenance
View Logs
bash# All services
docker-compose logs -f

# Specific service
docker-compose logs -f wazuh-mcp-server
docker-compose logs -f wazuh-client

# Last 100 lines
docker-compose logs --tail=100

# Since specific time
docker-compose logs --since 1h
Access Container Shell
bash# Server shell
docker-compose exec wazuh-mcp-server /bin/bash

# Client shell
docker-compose exec wazuh-client /bin/bash

# As root (for debugging)
docker-compose exec -u root wazuh-mcp-server /bin/bash
Update Images
bash# Pull latest base images
docker-compose pull

# Rebuild images
docker-compose build --pull

# Recreate containers
docker-compose up -d --force-recreate
Backup ChromaDB
bash# Create backup
tar czf chroma-backup-$(date +%Y%m%d).tar.gz rag_chroma/

# Restore backup
tar xzf chroma-backup-20240101.tar.gz
Clean Up
bash# Remove stopped containers
docker-compose down

# Remove with volumes (WARNING: deletes data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Clean everything
docker-compose down -v --rmi all
docker system prune -a
📊 Resource Usage
Check Resource Usage
bash# Real-time stats
docker stats

# Specific container
docker stats wazuh-mcp-server

# Format output
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
Set Resource Limits
Add to docker-compose.yml:
yamlservices:
  wazuh-mcp-server:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
🔒 Security Best Practices

Never commit .env file

bash   echo ".env" >> .gitignore

Use secrets for production

yaml   secrets:
     wazuh_password:
       file: ./secrets/wazuh_password.txt

Run as non-root (already configured)
Use HTTPS for Wazuh API (already in .env)
Rotate API keys regularly
Monitor container logs

📚 Additional Resources

Docker Documentation
Docker Compose Documentation
Wazuh Documentation
Multi-platform Builds

🆘 Getting Help
Quick Diagnostics
bash# 1. Check Docker
docker --version
docker-compose --version

# 2. Check services
docker-compose ps

# 3. Check logs
docker-compose logs --tail=50

# 4. Check environment
docker-compose config

# 5. Test connectivity
docker-compose exec wazuh-mcp-server curl http://localhost:8080/
Common Commands Reference
bash# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Shell
docker-compose exec wazuh-mcp-server /bin/bash

# Rebuild
docker-compose build --no-cache

# Status
docker-compose ps

# Client
docker attach wazuh-client
🎉 Success Checklist
✅ .env file exists with correct credentials
✅ docker-compose build completes without errors
✅ docker-compose up -d starts both services
✅ docker-compose ps shows services as "Up" and "healthy"
✅ curl http://localhost:8080/ returns HTTP 200
✅ docker attach wazuh-client connects successfully
✅ Client responds to queries with accurate data

You're all set! 🚀
For more detailed information, see the other documentation files in this package.
