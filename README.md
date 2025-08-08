# Healthcare AI Multi-Agent System 🏥

An intelligent healthcare system featuring 5 specialized AI agents powered by real machine learning models that communicate, debate, and collaborate to analyze patient data and provide clinical recommendations - just like a real medical team.

## 🚀 Quick Start

### Prerequisites
- Python 3.11 (recommended)
- Ollama (for LLM support)
- 4GB+ RAM
- GPU optional but recommended for faster processing

### Local Installation

```bash
# Clone the repository
git clone https://github.com/chandana-solix/healthcare-ai-multiagent-system.git
cd healthcare-ai-multiagent-system

# Create virtual environment (Python 3.11 recommended)
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Run the application
python intelligent_orchestrator.py
```

Access the application at: `http://localhost:8000`

## 🐳 Docker Deployment

### Using Docker

```bash
# Build the Docker image
docker build -t healthcare-ai .

# Run the container
docker run -p 8000:8000 healthcare-ai
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down
```

## 📁 Project Structure

```
healthcare-ai-multiagent-system/
├── agents/                 # AI agent implementations
│   ├── intelligent_lab_analyzer.py
│   ├── intelligent_image_analyzer.py
│   ├── intelligent_risk_stratification.py
│   ├── intelligent_clinical_decision.py
│   └── intelligent_consensus_builder.py
├── core/                   # Core system components
│   └── blackboard.py      # Agent communication system
├── static/                # Web UI files
│   ├── dashboard.html     # Main interface
│   └── patient_view.html  # Patient-friendly view
├── utils/                 # Utility modules
├── test_patients/         # Sample patient data
├── intelligent_orchestrator.py  # Main application
├── requirements.txt       # Python dependencies
├── requirements_docker.txt # Docker-specific versions
├── Dockerfile            # Docker configuration
└── docker-compose.yml    # Multi-container setup
```

## 🤖 AI Agents

The system features 5 specialized medical AI agents:

1. **Dr. LabTech** - Analyzes lab results using OCR
2. **Dr. Radiologist** - Analyzes X-rays using TorchXRayVision
3. **Dr. RiskAnalyst** - Performs risk stratification
4. **Dr. DecisionMaker** - Makes clinical decisions
5. **Dr. Consensus** - Builds consensus among agents

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# LLM Provider (ollama recommended for local/free usage)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434

# Optional: OpenAI API
# OPENAI_API_KEY=your-key-here
```

### Ollama Setup (Recommended)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required model
ollama pull llama2
```

## 📊 Features

- **Real AI Models**: TorchXRayVision for X-ray analysis, EasyOCR for lab extraction
- **Multi-Agent Collaboration**: Agents communicate via blackboard architecture
- **Risk Assessment**: SIRS, qSOFA, MEWS scoring
- **Patient-Friendly Views**: Simplified explanations for patients
- **GPU Support**: Automatic GPU detection (CUDA/MPS)

## 🧪 Testing

Upload sample files from `test_patients/` directory:
- Patient demographics (JSON)
- Lab report (image)
- Chest X-ray (image)

## 📝 API Endpoints

- `GET /` - Main dashboard
- `GET /patient` - Patient view
- `POST /analyze` - Analyze patient data
- `POST /patient_view` - Generate patient explanations
- `WS /ws` - WebSocket for real-time updates

## 🛠️ Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure you're using Python 3.11 and activated venv
2. **Ollama connection error**: Make sure Ollama is running (`ollama serve`)
3. **GPU not detected**: Install CUDA drivers or use CPU mode

### Requirements

- For exact working versions, use `requirements_docker.txt`
- Minimum Python version: 3.8 (3.11 recommended)
- Supported OS: Linux, macOS, Windows

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Docker Guide](DOCKER_GUIDE.md)
- [File Structure Guide](FILE_GUIDE.md)
- [Test Data Guide](TEST_DATA_GUIDE.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- TorchXRayVision for X-ray analysis
- EasyOCR for text extraction
- Ollama for local LLM support

---

**Note**: This system is for educational/demonstration purposes. Not for actual medical diagnosis.