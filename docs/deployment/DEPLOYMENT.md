# Docker Deployment Guide

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Building the Image](#building-the-image)
- [Running the Container](#running-the-container)
- [Management](#management)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

---

## 🚀 Quick Start

### Option 1: Using Deployment Script (Recommended)

```bash
# 1. Configure environment
cp .env.example .env
nano .env  # Add your API keys

# 2. Deploy everything
./deploy.sh

# 3. Access the application
open http://localhost:8000
```

### Option 2: Using Docker Compose

```bash
# 1. Configure environment
cp .env.example .env
nano .env  # Add your API keys

# 2. Build and start
docker-compose up -d --build

# 3. View logs
docker-compose logs -f web

# 4. Access the application
open http://localhost:8000
```

### Option 3: Using Docker Directly

```bash
# 1. Build image
docker build -t screenplay-analysis:latest .

# 2. Run container
docker run -d \
  --name screenplay-web \
  -p 8000:8000 \
  -v $(pwd)/.env:/app/.env:ro \
  -v screenplay-data:/data \
  screenplay-analysis:latest

# 3. View logs
docker logs -f screenplay-web

# 4. Access the application
open http://localhost:8000
```

---

## 📦 Prerequisites

### Required Software

- **Docker**: Version 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 1.29+ (optional, but recommended)

### Check Installation

```bash
docker --version
docker-compose --version
```

### System Requirements

- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB free space
- **OS**: Linux, macOS, or Windows with WSL2

---

## ⚙️ Configuration

### 1. Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure the following:

```bash
# Required: DeepSeek API Key (default provider)
DEEPSEEK_API_KEY=your_api_key_here

# Optional: Other LLM providers
# ANTHROPIC_API_KEY=your_anthropic_key
# OPENAI_API_KEY=your_openai_key

# Optional: LangSmith observability
LANGCHAIN_TRACING_V2=false
# LANGCHAIN_API_KEY=your_langsmith_key
# LANGCHAIN_PROJECT=screenplay-analysis-prod
```

### 2. Port Configuration

Default port is `8000`. To change it:

**Docker Compose:**
Edit `docker-compose.yml`:
```yaml
ports:
  - "9000:8000"  # Change 9000 to your desired port
```

**Docker Run:**
```bash
docker run -p 9000:8000 ...  # Change 9000 to your desired port
```

---

## 🏗️ Building the Image

### Build with Docker Compose

```bash
docker-compose build --no-cache
```

### Build with Docker

```bash
docker build -t screenplay-analysis:latest .
```

### Build with Custom Tag

```bash
docker build -t screenplay-analysis:v2.4.0 .
```

### Build Arguments (if needed)

```bash
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  -t screenplay-analysis:latest .
```

---

## 🚀 Running the Container

### Start Container

**Using deployment script:**
```bash
./deploy.sh start
```

**Using Docker Compose:**
```bash
docker-compose up -d
```

**Using Docker:**
```bash
docker run -d \
  --name screenplay-web \
  -p 8000:8000 \
  -v $(pwd)/.env:/app/.env:ro \
  -v screenplay-data:/data \
  -v $(pwd)/examples:/app/examples:ro \
  --restart unless-stopped \
  screenplay-analysis:latest
```

### Verify Container is Running

```bash
# Check container status
docker ps | grep screenplay-web

# Check health endpoint
curl http://localhost:8000/health

# View logs
docker logs screenplay-web
```

---

## 🔧 Management

### Using Deployment Script

```bash
# Deploy (build + start)
./deploy.sh deploy

# Build image only
./deploy.sh build

# Start container
./deploy.sh start

# Stop container
./deploy.sh stop

# Restart container
./deploy.sh restart

# View logs
./deploy.sh logs

# Check status
./deploy.sh status
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f web

# View logs (last 100 lines)
docker-compose logs --tail=100 web

# Rebuild and restart
docker-compose up -d --build

# Stop and remove volumes
docker-compose down -v
```

### Using Docker Commands

```bash
# Start container
docker start screenplay-web

# Stop container
docker stop screenplay-web

# Restart container
docker restart screenplay-web

# View logs
docker logs -f screenplay-web

# View logs (last 100 lines)
docker logs --tail=100 screenplay-web

# Execute command in container
docker exec -it screenplay-web bash

# Remove container
docker rm -f screenplay-web

# Remove image
docker rmi screenplay-analysis:latest
```

---

## 🐛 Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker logs screenplay-web
```

**Common issues:**
1. **Port already in use:**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   # Kill process or change port
   ```

2. **Missing .env file:**
   ```bash
   cp .env.example .env
   # Edit .env and add API keys
   ```

3. **Permission errors:**
   ```bash
   # Ensure .env is readable
   chmod 644 .env
   ```

### Health Check Failing

```bash
# Check if container is running
docker ps | grep screenplay-web

# Check health endpoint manually
curl -v http://localhost:8000/health

# Check application logs
docker logs screenplay-web

# Check network
docker inspect screenplay-web | grep IPAddress
```

### Cannot Access Web UI

1. **Check container status:**
   ```bash
   docker ps
   ```

2. **Check port mapping:**
   ```bash
   docker port screenplay-web
   ```

3. **Check firewall:**
   ```bash
   # Allow port 8000
   sudo ufw allow 8000
   ```

4. **Try accessing via container IP:**
   ```bash
   CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' screenplay-web)
   curl http://$CONTAINER_IP:8000
   ```

### Python Errors

**View detailed error logs:**
```bash
docker logs --tail=200 screenplay-web
```

**Access container shell:**
```bash
docker exec -it screenplay-web bash

# Inside container:
python -m src.cli --help
pytest tests/
```

### Data Persistence Issues

**Check volume:**
```bash
# List volumes
docker volume ls | grep screenplay

# Inspect volume
docker volume inspect screenplay-data

# Remove volume (WARNING: deletes data)
docker volume rm screenplay-data
```

---

## 🌐 Production Deployment

### Security Best Practices

1. **Use secrets management:**
   ```bash
   # Don't commit .env file
   echo ".env" >> .gitignore

   # Use Docker secrets (Swarm mode)
   docker secret create deepseek_key .env
   ```

2. **Run with limited permissions:**
   - Container already runs as non-root user (`appuser`)
   - Read-only filesystem for config files

3. **Enable HTTPS:**
   Use a reverse proxy (Nginx, Traefik, Caddy)

### Reverse Proxy Example (Nginx)

```nginx
server {
    listen 80;
    server_name screenplay.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Docker Swarm Deployment

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml screenplay

# Check services
docker service ls

# View logs
docker service logs -f screenplay_web
```

### Resource Limits

Edit `docker-compose.yml`:

```yaml
services:
  web:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Monitoring

```bash
# Container stats
docker stats screenplay-web

# Health check
watch -n 5 'curl -s http://localhost:8000/health | jq'

# Enable LangSmith monitoring (edit .env)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=screenplay-production
```

### Backup

```bash
# Backup data volume
docker run --rm \
  -v screenplay-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/screenplay-data-$(date +%Y%m%d).tar.gz /data

# Restore from backup
docker run --rm \
  -v screenplay-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/screenplay-data-20251114.tar.gz -C /
```

---

## 📊 Monitoring and Logs

### View Real-time Logs

```bash
# All logs
docker logs -f screenplay-web

# Filter by level
docker logs screenplay-web 2>&1 | grep ERROR

# Save to file
docker logs screenplay-web > logs.txt 2>&1
```

### Container Metrics

```bash
# CPU, Memory, Network
docker stats screenplay-web

# Full stats (JSON)
docker stats --no-stream --format "{{json .}}" screenplay-web | jq
```

---

## 🔄 Updates and Maintenance

### Update to Latest Version

```bash
# Pull latest code
git pull

# Rebuild and restart
./deploy.sh deploy

# Or with docker-compose
docker-compose up -d --build
```

### Clean Up Old Images

```bash
# Remove unused images
docker image prune

# Remove all unused resources
docker system prune -a
```

---

## 📚 Additional Resources

- **Application Docs**: See `CLAUDE.md` for full documentation
- **API Reference**: See `ref/api-reference.md`
- **Docker Docs**: https://docs.docker.com/
- **Docker Compose Docs**: https://docs.docker.com/compose/

---

## 💡 Tips

1. **Development Mode**: Mount source code as volume for hot-reload:
   ```bash
   docker run -v $(pwd):/app ...
   ```

2. **Custom Configuration**: Override environment variables:
   ```bash
   docker run -e LLM_PROVIDER=anthropic ...
   ```

3. **Multiple Instances**: Run on different ports:
   ```bash
   docker run -p 8001:8000 --name screenplay-web-2 ...
   ```

---

## 🆘 Support

If you encounter issues:

1. Check this troubleshooting guide
2. Review container logs: `docker logs screenplay-web`
3. Check health endpoint: `curl http://localhost:8000/health`
4. Open an issue on GitHub with logs and configuration

---

**Version**: 2.4.0
**Last Updated**: 2025-11-14
