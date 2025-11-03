# Docker Deployment Guide

This guide covers running Perplexity API Simple in Docker, both locally and on cloud platforms like AWS.

## Quick Start (Local)

### Prerequisites
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)
- Perplexity account with valid cookie

### 1. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Perplexity cookie
nano .env  # or use your preferred editor
```

Get your Perplexity cookie:
1. Login to https://www.perplexity.ai
2. Open DevTools (F12)
3. Go to Application/Storage → Cookies
4. Copy the entire cookie string (all fields semicolon-separated)
5. Paste into `.env` file as `PERPLEXITY_COOKIE=your-cookie-here`

### 2. Start the Server

```bash
# Build and start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 3. Access the Dashboard

Open http://localhost:8765 in your browser to:
- Generate API keys
- Update your Perplexity cookie (with hot-reload)
- View usage statistics

### 4. Test the API

```bash
# Health check
curl http://localhost:8765/health

# Test search endpoint (generate an API key first from the dashboard)
curl -X POST http://localhost:8765/search \
  -H "Authorization: Bearer pplx_your-key-here" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Docker?", "mode": "auto"}'
```

## Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f perplexity-api

# Restart after configuration changes
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build

# Remove everything (including volumes)
docker-compose down -v
```

## Development Mode

For active development with live code reloading:

1. Edit `docker-compose.yml` and uncomment the development volume mounts:

```yaml
volumes:
  - ./src:/app/src
  - ./web:/app/web
```

2. Restart the container:

```bash
docker-compose restart
```

Now changes to `src/` and `web/` will be reflected in the running container.

## Persistent Data

The following data persists across container restarts via volumes:

- **API Keys**: `.api_keys.json` - All generated API keys
- **Configuration**: `.env` - Server configuration and Perplexity cookie

These files are mounted as volumes in `docker-compose.yml`.

## Cloud Deployment (AWS)

### Option 1: EC2 with Docker Compose

#### 1. Launch EC2 Instance

```bash
# Amazon Linux 2023 or Ubuntu 22.04
# Instance type: t2.micro (1GB RAM) or larger
# Security group: Allow inbound on port 8765
```

#### 2. Install Docker

```bash
# For Amazon Linux 2023
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in for group changes to take effect
```

#### 3. Deploy Application

```bash
# Clone repository
git clone <your-repo-url>
cd perplexity-api-simple

# Configure environment
cp .env.example .env
nano .env  # Add PERPLEXITY_COOKIE

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### 4. Configure Security Group

Allow inbound traffic on port 8765:
- Type: Custom TCP
- Port: 8765
- Source: Your IP or 0.0.0.0/0 (less secure)

#### 5. Access Your Server

```bash
# Get EC2 public IP
curl http://checkip.amazonaws.com

# Access dashboard
http://<EC2-PUBLIC-IP>:8765
```

### Option 2: AWS ECS/Fargate

#### 1. Build and Push to ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name perplexity-api-simple

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t perplexity-api-simple .

# Tag image
docker tag perplexity-api-simple:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/perplexity-api-simple:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/perplexity-api-simple:latest
```

#### 2. Create ECS Task Definition

Create `task-definition.json`:

```json
{
  "family": "perplexity-api-simple",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "perplexity-api",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/perplexity-api-simple:latest",
      "portMappings": [
        {
          "containerPort": 8765,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "PORT",
          "value": "8765"
        },
        {
          "name": "HOST",
          "value": "0.0.0.0"
        }
      ],
      "secrets": [
        {
          "name": "PERPLEXITY_COOKIE",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<account-id>:secret:perplexity-cookie"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/perplexity-api-simple",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 3. Store Cookie in Secrets Manager

```bash
# Create secret for Perplexity cookie
aws secretsmanager create-secret \
  --name perplexity-cookie \
  --description "Perplexity authentication cookie" \
  --secret-string "your-cookie-here"
```

#### 4. Create ECS Service

```bash
# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create ECS cluster (if not exists)
aws ecs create-cluster --cluster-name perplexity-cluster

# Create service
aws ecs create-service \
  --cluster perplexity-cluster \
  --service-name perplexity-api-service \
  --task-definition perplexity-api-simple \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Option 3: AWS App Runner

App Runner provides the simplest deployment with automatic builds from source:

```bash
# Create apprunner.yaml in project root
cat > apprunner.yaml <<EOF
version: 1.0
runtime: python3
build:
  commands:
    build:
      - pip install -r requirements.txt
run:
  command: python src/perplexity_api_server.py
  network:
    port: 8765
    env: PORT
  env:
    - name: PORT
      value: "8765"
    - name: HOST
      value: "0.0.0.0"
EOF

# Deploy via AWS Console or CLI
# Note: Add PERPLEXITY_COOKIE as environment variable in App Runner configuration
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PERPLEXITY_COOKIE` | Yes | - | Full cookie string from Perplexity.ai |
| `PORT` | No | 8765 | Port to run the server on |
| `HOST` | No | 0.0.0.0 | Host to bind the server to |

## Networking

### Port Mapping

The container exposes port 8765. You can map it to different host ports:

```bash
# Map to port 80
PORT=80 docker-compose up -d

# Or edit docker-compose.yml:
ports:
  - "80:8765"
```

### Reverse Proxy (Nginx)

For production deployments behind Nginx:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring

### Health Checks

The container includes built-in health checks:

```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' perplexity-api-server

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' perplexity-api-server
```

### Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100

# View logs for specific service
docker-compose logs perplexity-api
```

### Resource Usage

```bash
# View resource usage
docker stats perplexity-api-server

# Detailed container info
docker inspect perplexity-api-server
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs

# Verify .env file exists and has PERPLEXITY_COOKIE
cat .env

# Check if port is already in use
lsof -i :8765  # or netstat -tulpn | grep 8765
```

### Cannot Connect to Server

```bash
# Verify container is running
docker-compose ps

# Check health status
docker inspect --format='{{.State.Health.Status}}' perplexity-api-server

# Test from inside container
docker exec -it perplexity-api-server curl http://localhost:8765/health

# Check firewall rules (AWS Security Groups, iptables, etc.)
```

### Cookie Authentication Failing

```bash
# Update cookie via web dashboard at http://localhost:8765
# Or update .env and restart:
docker-compose restart
```

### API Keys Not Persisting

```bash
# Verify volume mount exists
docker-compose config | grep -A 2 volumes

# Check file permissions
ls -la .api_keys.json

# If missing, touch the file:
touch .api_keys.json
docker-compose restart
```

## Production Best Practices

1. **Use Secrets Manager**: Store `PERPLEXITY_COOKIE` in AWS Secrets Manager or similar
2. **Enable HTTPS**: Use SSL/TLS certificates (Let's Encrypt, AWS Certificate Manager)
3. **Set Up Monitoring**: Use CloudWatch, Datadog, or Prometheus
4. **Configure Backups**: Back up `.api_keys.json` regularly
5. **Limit Access**: Use security groups/firewall rules to restrict access
6. **Use Fixed Tags**: Pin Docker image versions instead of `latest`
7. **Enable Auto-Restart**: Set `restart: unless-stopped` in docker-compose.yml (already configured)

## Next Steps

- See [README.md](README.md) for API usage documentation
- See [CLAUDE.md](CLAUDE.md) for Claude Code integration
- See [docs/API_ENDPOINTS.md](docs/API_ENDPOINTS.md) for detailed endpoint documentation

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review [troubleshooting section](#troubleshooting)
- Open an issue on GitHub
