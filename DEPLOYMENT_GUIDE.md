# Healthcare AI System - Deployment Guide

## ⚡ QUICK START FOR DEPLOYMENT

### Which Branch to Deploy?
**USE: `ml-integration` branch** - This has the complete AI-powered system with ML models.

```bash
git clone https://github.com/chandana-solix/healthcare-ai-multiagent-system.git
cd healthcare-ai-multiagent-system
git checkout ml-integration  # ← IMPORTANT: Use this branch!
```

### Why ml-integration branch?
- ✅ Has TorchXRayVision for X-ray analysis
- ✅ Has EasyOCR for lab report reading
- ✅ GPU support enabled
- ✅ All ML dependencies configured
- ✅ Production-ready

### Why NOT main branch?
- ❌ No ML models (commented out)
- ❌ Only rule-based logic
- ❌ No GPU support

## 🚀 Deployment Steps

1. **Clone and checkout ml-integration**:
```bash
git checkout ml-integration
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the system**:
```bash
python intelligent_orchestrator.py
```

## 📦 For Docker Deployment
Use the ml-integration branch and the included Dockerfile.

---
**Contact**: If any confusion, deploy `ml-integration` branch - it's the complete version!
