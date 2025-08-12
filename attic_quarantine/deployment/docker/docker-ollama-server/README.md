# External Ollama Server for PromptEvolver

This directory contains deployment configurations for running Ollama + Qwen3:4b on an external server that Convex can access.

## Quick Deploy Options

### Option 1: Docker Compose (Recommended)

```bash
# Build and start the server
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f ollama-server

# Test the server
curl http://localhost:11434/api/tags
```

### Option 2: Manual VPS Setup

```bash
# Copy deployment script to your VPS
scp ../deploy-ollama-server.sh user@your-vps:/tmp/

# SSH to your VPS and run
ssh user@your-vps
sudo /tmp/deploy-ollama-server.sh
```

### Option 3: Cloud Deployment Services

**Railway:**

- Connect this repository
- Set `DOCKERFILE_PATH=docker-ollama-server/Dockerfile`
- Deploy (provides public URL automatically)

**DigitalOcean App Platform:**

- Create new app from GitHub
- Set build context to `docker-ollama-server/`
- Deploy

**Google Cloud Run:**

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/ollama-server docker-ollama-server/
gcloud run deploy --image gcr.io/PROJECT_ID/ollama-server --port 11434
```

## Configuration

Once deployed, update your Convex environment:

```bash
# In your nextjs-app/.env.local
OLLAMA_SERVER_URL=http://YOUR_SERVER_IP:11434

# Or set in Convex dashboard under Environment Variables
OLLAMA_SERVER_URL=http://YOUR_SERVER_IP:11434
```

## Testing the Deployment

```bash
# Test basic connectivity
curl http://YOUR_SERVER_IP:11434/api/tags

# Test model generation
curl http://YOUR_SERVER_IP:11434/api/generate \
  -d '{
    "model": "qwen3:4b",
    "prompt": "Hello, how are you?",
    "stream": false
  }'
```

## Security Considerations

- This setup exposes Ollama on a public port
- Consider adding authentication proxy for production
- Use HTTPS in production environments
- Monitor resource usage (Qwen3:4b requires ~2.6GB RAM)

## Resource Requirements

- **Minimum**: 4GB RAM, 2 vCPU, 10GB storage
- **Recommended**: 8GB RAM, 4 vCPU, 20GB storage
- **Model Size**: Qwen3:4b is ~2.6GB

## Troubleshooting

```bash
# Check container logs
docker-compose logs ollama-server

# Check model availability
docker exec promptevolver-ollama ollama list

# Restart service
docker-compose restart ollama-server

# Clean restart (re-downloads model)
docker-compose down -v
docker-compose up -d
```
