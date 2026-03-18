# 🐳 Docker Deployment Guide

## Quick Start

### Prerequisites
- Docker Desktop installed
- 8GB RAM minimum
- 10GB free disk space

### One-Command Setup

**Windows:**
```cmd
docker-setup.bat
```

**Linux/Mac:**
```bash
chmod +x docker-setup.sh
./docker-setup.sh
```

Then open: http://localhost:8501

---

## Manual Setup

### 1. Build and Start
```bash
docker-compose up -d
```

### 2. Download AI Model
```bash
docker exec papermind-ollama ollama pull llama3.2:3b
```

### 3. Access Application

Open browser: http://localhost:8501

---

## Container Management

### View Logs
```bash
docker-compose logs -f papermind
```

### Stop Services
```bash
docker-compose down
```

### Restart
```bash
docker-compose restart
```

### Shell Access
```bash
docker exec -it papermind-app bash
```

### Remove Everything
```bash
docker-compose down -v
```

---

## Architecture
```
┌─────────────────┐
│   Browser       │
│  localhost:8501 │
└────────┬────────┘
         │
    ┌────▼────────────┐
    │  PaperMind App  │
    │  (Streamlit)    │
    └────┬────────────┘
         │
    ┌────▼─────────┐
    │   Ollama     │
    │ (Local LLM)  │
    └──────────────┘
```

---

## Volumes

- `./data` - Research papers and vector database
- `./logs` - Application logs
- `ollama-data` - AI model storage

---

## Troubleshooting

### Container won't start
```bash
docker-compose logs papermind
```

### Out of memory
Increase Docker memory limit to 8GB in Docker Desktop settings.

### Port already in use
Edit `docker-compose.yml` and change port `8501` to another port.

### Ollama connection failed
```bash
docker-compose restart ollama
docker exec papermind-ollama ollama pull llama3.2:3b
```

---

## Environment Variables

Edit `.env` file:
```env
USE_LOCAL_LLM=true
LLM_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://ollama:11434
MAX_PAPERS_PER_QUERY=5
```

---

## Production Deployment

For production:

1. Use reverse proxy (nginx)
2. Enable HTTPS
3. Set resource limits
4. Configure backups
5. Monitor logs

---

## Development

Mount code as volume for live reload:
```yaml
volumes:
  - .:/app
```

Then restart container after code changes.