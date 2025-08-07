# Docker Deployment Guide

## 🐳 Quick Start with Docker

### Prerequisites
- Docker installed
- Docker Compose installed
- NVIDIA Container Toolkit (for GPU support)

### 1. Build and Run

```bash
# Simple run (CPU only)
docker-compose up --build

# Run in background
docker-compose up -d --build

# With GPU support (Linux/Windows)
docker-compose up --build --gpus all
```

### 2. Access the System
Open http://localhost:8000 in your browser

### 3. Stop the System
```bash
docker-compose down
```

## 🚀 Deployment Options

### Option 1: Using Docker Compose (Recommended)
```bash
# Clone repository
git clone https://github.com/chandana-solix/healthcare-ai-multiagent-system.git
cd healthcare-ai-multiagent-system

# Build and run
docker-compose up --build
```

### Option 2: Using Dockerfile Only
```bash
# Build image
docker build -t healthcare-ai .

# Run container
docker run -p 8000:8000 healthcare-ai

# Run with GPU
docker run --gpus all -p 8000:8000 healthcare-ai
```

### Option 3: Pull from Registry (If Published)
```bash
docker pull your-registry/healthcare-ai:latest
docker run -p 8000:8000 your-registry/healthcare-ai:latest
```

## 📁 Volume Mounts

The docker-compose.yml includes:
- `./uploads:/app/uploads` - Persists uploaded files
- `./test_data:/app/test_data` - Mount test patient data

## 🔧 Environment Variables

Set in docker-compose.yml or pass via -e:
```bash
docker run -e LLM_PROVIDER=openai -e OPENAI_API_KEY=xxx healthcare-ai
```

## 🖥️ GPU Support

### For NVIDIA GPUs:
1. Install NVIDIA Container Toolkit
2. The compose file already includes GPU configuration

### For Mac (M1/M2/M3):
- Docker Desktop doesn't support MPS passthrough
- Will run on CPU inside container
- Still faster than most laptops

## 🐛 Troubleshooting

### Port already in use:
```bash
# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Use 8080 instead
```

### Out of memory:
Add to docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      memory: 8G
```

### GPU not detected:
```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

## 📦 Production Deployment

For production, consider:
1. Use specific version tags
2. Set up health checks
3. Configure logging
4. Use secrets management
5. Set up reverse proxy (nginx)

## 🔄 Updating

```bash
# Pull latest code
git pull

# Rebuild container
docker-compose up --build
```
