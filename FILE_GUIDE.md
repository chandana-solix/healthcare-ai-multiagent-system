# 📁 Healthcare AI System - Complete File Guide

## 🎯 **Core Application Files**

### **`intelligent_orchestrator.py`**
- **What it is**: Main application entry point
- **Purpose**: Starts the web server, handles WebSocket connections, coordinates all agents
- **Important**: This is what you run to start the system (`python intelligent_orchestrator.py`)

### **`healthcare_ai_complete_all_fixes.py`**
- **What it is**: ML model implementations
- **Purpose**: Contains TorchXRayVision and EasyOCR integration code
- **Important**: Has GPU detection and model loading logic

### **`config.py`**
- **What it is**: System configuration
- **Purpose**: API keys, model paths, system settings
- **Important**: Modify this for different environments

---

## 🤖 **Agent Files** (`agents/` folder)

### **`intelligent_lab_analyzer.py`**
- **Purpose**: Analyzes blood tests, extracts values using OCR
- **Key feature**: Uses EasyOCR to read lab reports

### **`intelligent_image_analyzer.py`**
- **Purpose**: Analyzes X-rays for 18 different pathologies
- **Key feature**: Uses TorchXRayVision AI model

### **`intelligent_risk_stratification.py`**
- **Purpose**: Calculates risk scores (SIRS, qSOFA, MEWS)
- **Key feature**: Determines if patient needs ICU

### **`intelligent_clinical_decision.py`**
- **Purpose**: Makes treatment recommendations
- **Key feature**: Prescribes medications, decides admission

### **`intelligent_consensus_builder.py`**
- **Purpose**: Ensures all agents agree on diagnosis
- **Key feature**: Handles disagreements between agents

### **Patient View Agents** (for generating explanations):
- `test_results_explainer.py` - Explains lab results
- `enhanced_patient_view.py` - Creates patient-friendly explanations
- `hybrid_patient_view.py` - Combines AI and template responses

---

## 🌐 **UI Files** (`static/` folder)

### **`dashboard.html`**
- **What it is**: Main web interface
- **Purpose**: Upload patient data, start analysis
- **Critical**: Without this, no web interface!

### **`patient_view.html`**
- **What it is**: Results display page
- **Purpose**: Shows diagnosis, treatment plan, patient explanation
- **Critical**: Without this, can't see results!

### **`sample_demographics.json`**
- **What it is**: Example patient data format
- **Purpose**: Shows correct JSON structure for patient info

---

## 🐳 **Docker Files**

### **`Dockerfile`**
- **What it is**: Docker image blueprint
- **Purpose**: Tells Docker how to build the container
- **Contains**: Python version, dependencies, setup commands

### **`docker-compose.yml`**
- **What it is**: Docker orchestration file
- **Purpose**: Easy way to run with `docker-compose up`
- **Contains**: Port mapping, environment variables

### **`.dockerignore`**
- **What it is**: Tells Docker what to exclude
- **Purpose**: Keeps image size small by excluding venv, cache

---

## 📋 **Setup & Configuration**

### **`requirements.txt`**
- **What it is**: Python dependencies list
- **Purpose**: Install with `pip install -r requirements.txt`
- **Contains**: FastAPI, PyTorch, EasyOCR, etc.

### **`.env.example`**
- **What it is**: Environment variable template
- **Purpose**: Copy to `.env` and add your API keys
- **Note**: `.env` not in Git for security

### **`setup.sh`**
- **What it is**: Quick setup script
- **Purpose**: Installs dependencies, sets up environment

### **`setup_ollama.sh`**
- **What it is**: AI model setup
- **Purpose**: Installs Ollama for AI explanations

---

## 📚 **Documentation**

### **`README.md`**
- **Main project documentation**
- Start here for overview

### **`INTELLIGENT_SYSTEM_README.md`**
- **Detailed system architecture**
- Explains how agents work

### **`DEPLOYMENT_GUIDE.md`**
- **How to deploy to production**
- Server requirements, setup steps

### **`DOCKER_GUIDE.md`**
- **Docker-specific instructions**
- How to build and run containers

### **`TEST_DATA_GUIDE.md`**
- **How to use test patient data**
- Format for demographics, lab reports, X-rays

### **`RUN_INSTRUCTIONS.md`**
- **Quick start guide**
- Step-by-step to run locally

---

## 🧪 **Testing & Utilities**

### **`test_ml.py`**
- **Tests if ML models load correctly**
- Run this to verify PyTorch, TorchXRayVision work

### **`test_gpu.py`**
- **Checks GPU availability**
- Detects CUDA or Apple Silicon

### **`verify_ml.py`**
- **Comprehensive ML verification**
- Tests all models end-to-end

### **`run.sh`**
- **Quick launch script**
- Shortcut to start the system

---

## 📂 **Important Folders**

### **`core/`**
- Contains `blackboard.py` - agent communication system

### **`utils/`**
- Helper functions for medical analysis
- AI integration utilities

### **`test_patients/`**
- 30 test patient datasets
- Use these for testing

### **`uploads/`**
- Temporary storage for uploaded files
- Gets created automatically

---

## 💡 **Quick Start Guide**

### **To run locally**:
```bash
# Clone the repository
git clone https://github.com/chandana-solix/healthcare-ai-multiagent-system.git
cd healthcare-ai-multiagent-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python intelligent_orchestrator.py

# Open browser to http://localhost:8000
```

### **To run with Docker**:
```bash
# Build the Docker image
docker build -t healthcare-ai .

# Run the container
docker run -p 8000:8000 healthcare-ai

# Open browser to http://localhost:8000
```

### **System Requirements**:
- Python 3.8+
- 8-12GB RAM (for ML models)
- 2GB disk space (for model downloads)

### **First Run**:
- Models download automatically (~500MB)
- Takes 2-3 minutes on first start
- Subsequent runs are faster

---

## 🔧 **Troubleshooting**

### **If EasyOCR fails in Docker on Mac**:
- Known issue with ARM64 processors
- Run natively with `python intelligent_orchestrator.py`

### **If models don't load**:
- Check internet connection (first run downloads models)
- Verify 8GB+ RAM available
- Run `python test_ml.py` to diagnose

### **If web UI doesn't appear**:
- Check `static/` folder has dashboard.html
- Verify port 8000 is not in use
- Check browser console for errors

---

## 📞 **Support**

For issues or questions:
1. Check existing documentation
2. Run test scripts (`test_ml.py`, `verify_ml.py`)
3. Review error messages in terminal
4. Contact team with specific error details

---

**Last Updated**: January 2025
**Version**: 1.0
**Repository**: https://github.com/chandana-solix/healthcare-ai-multiagent-system
