# Healthcare AI Multi-Agent System

An intelligent healthcare system featuring 5 specialized AI agents that communicate, debate, and collaborate to analyze patient data and provide clinical recommendations - just like a real medical team.

## 🏥 Overview

This system demonstrates how multiple AI agents can work together to solve complex medical cases. Each agent has specialized medical knowledge and can:
- 🗣️ Communicate with other agents in real-time
- 🤔 Ask questions and debate findings  
- 🤝 Build consensus on diagnoses and treatment
- 🚨 Alert the team to critical findings
- 📊 Calculate real clinical risk scores

## ✨ Key Features

### Intelligent Multi-Agent System
- **5 Specialized Medical Agents** that act like a virtual medical team
- **Real-time Agent Communication** - watch agents discuss and debate
- **Blackboard Architecture** - shared knowledge space for collaboration
- **Clinical Scoring Systems** - SIRS, CURB-65, MEWS, qSOFA
- **Pattern Recognition** - detects sepsis, pneumonia, cardiac issues
- **Consensus Building** - agents vote and reach agreement

### Medical Intelligence
- Evidence-based clinical thresholds and guidelines
- Automatic risk stratification (LOW/MODERATE/HIGH/CRITICAL)
- Treatment recommendations with antibiotic selection
- Kidney function calculations with dosing adjustments
- Critical value detection and alerts

### Technical Features
- **Real-time Updates** via WebSockets - see agents communicate live
- **Graceful Fallbacks** - works without AI models using templates
- **No Database Required** - upload files and get instant analysis
- **Modern Web Interface** - dark theme optimized for medical use
- **Extensible Architecture** - easy to add new specialist agents

### Patient View - Personalized Healthcare Insights
- **Emergency Alerts** - Clear, color-coded alerts for critical conditions
- **Admission Explanations** - Why hospitalization is needed in plain language
- **Cost Transparency** - Detailed breakdown of expected medical costs
- **Insurance Estimates** - What you'll likely pay with insurance coverage
- **Treatment Options** - Alternative approaches with pros and cons
- **Personalized Warnings** - Red flags specific to your condition
- **Questions to Ask** - Important questions for your doctor
- **Recovery Timeline** - What to expect during treatment

## 🚀 Quick Start

### Simple Setup (3 steps)

1. **Clone the repository**
```bash
git clone <repository-url>
cd healthcare-ai-multiagent-system
```

2. **Install dependencies**
```bash
pip3 install -r requirements.txt
```

3. **Run the server**
```bash
python3 intelligent_orchestrator.py
```

That's it! Open http://localhost:8000 in your browser.

### Optional: Enable AI Models

For enhanced AI capabilities (not required):
```bash
# Install Ollama (free, runs locally)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2

# Or use OpenAI (requires API key)
cp .env.example .env
# Edit .env and add OPENAI_API_KEY
```

## 🏗️ Architecture

### System Design

```
┌─────────────────────┐     ┌───────────────────────┐     ┌──────────────────┐
│   Web Interface     │ ──► │   FastAPI Backend     │ ──► │  Blackboard      │
│  (HTML/JS/CSS)      │ ◄── │  (Orchestrator)       │ ◄── │  Message Bus     │
└─────────────────────┘     └───────────────────────┘     └──────────────────┘
         │                              │                            │
         │ WebSocket                    │                            │
         └──────────────────────────────┘                           │
                                                                     │
┌──────────────────────────────────────────────────────────────────┴─────────┐
│                          Agent Communication Layer                          │
├─────────────┬──────────────┬──────────────┬─────────────┬────────────────┤
│ Lab Analyzer│Image Analyzer│Risk Assessor │Clinical     │Consensus       │
│ Agent       │Agent         │Agent         │Decision     │Builder         │
│             │              │              │Agent        │Agent           │
└─────────────┴──────────────┴──────────────┴─────────────┴────────────────┘
```

### The 5 Medical Agents

1. **Lab Analyzer Agent** ("Dr. LabTech")
   - Analyzes blood tests and identifies critical values
   - Detects infection patterns and organ dysfunction
   - Asks other agents about correlating findings

2. **Image Analyzer Agent** ("Dr. Radiology")
   - Interprets chest X-rays and medical images
   - Identifies pneumonia, consolidations, effusions
   - Correlates imaging with lab findings

3. **Risk Stratification Agent** ("Dr. RiskAssessor")
   - Calculates validated clinical scores
   - Monitors for deterioration risk
   - Recommends appropriate level of care

4. **Clinical Decision Agent** ("Dr. DecisionMaker")
   - Synthesizes all findings into diagnoses
   - Creates evidence-based treatment plans
   - Considers patient factors (age, allergies)

5. **Consensus Builder Agent** ("Dr. Consensus")
   - Facilitates agreement between agents
   - Resolves conflicting opinions
   - Creates unified action plans

### Communication Example

```
[Dr. LabTech] 🔬 "Critical finding: WBC 18.5, CRP 145 - severe infection!"
[Dr. LabTech] ❓ "Dr. Radiology, do you see any signs of pneumonia?"
[Dr. Radiology] 🩻 "Yes! Right lower lobe consolidation confirmed"
[Dr. RiskAssessor] ⚡ "CURB-65 score 4/5 - HIGH RISK patient"
[Dr. DecisionMaker] 🏥 "Recommending ICU admission with IV antibiotics"
[Dr. Consensus] 🤝 "All agents agree: ICU admission for severe pneumonia"
```

## 📁 Project Structure

```
healthcare-ai-multiagent-system/
├── intelligent_orchestrator.py  # Main application server
├── agents/                      # AI agents
│   ├── intelligent_lab_analyzer.py
│   ├── intelligent_image_analyzer.py
│   ├── intelligent_risk_stratification.py
│   ├── intelligent_clinical_decision.py
│   └── intelligent_consensus_builder.py
├── core/
│   └── blackboard.py           # Agent communication system
├── utils/
│   ├── medical_intelligence.py # Clinical knowledge base
│   └── llm_integration.py      # AI model integration
├── static/                     # Web interface
│   ├── dashboard.html          # Main dashboard
│   └── patient_view.html       # Patient analysis view
├── test_patients/              # Sample test cases
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# LLM Provider (optional - system works without it)
LLM_PROVIDER=ollama  # Options: ollama, openai, none

# Ollama Configuration (if using)
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI Configuration (if using)
# OPENAI_API_KEY=your-key-here

# Server Configuration
PORT=8000
HOST=0.0.0.0
```

## 🎯 Usage

### 1. Upload Patient Data

The system accepts three files:
- **Demographics**: JSON file with patient info and vitals
- **Lab Report**: Image of blood test results
- **Chest X-ray**: Medical imaging file

### 2. Watch Agents Collaborate

Once uploaded, watch as agents:
- Analyze their specialized areas
- Share findings on the blackboard
- Ask each other clarifying questions
- Debate different interpretations
- Build consensus on the diagnosis

### 3. Get Comprehensive Results

Receive:
- Primary diagnosis with confidence level
- Risk assessment and severity scores
- Treatment recommendations
- Admission decisions
- Cost estimates
- Action plan with immediate steps

### 4. View Patient-Friendly Explanations

Access the **Patient View** for:
- **Plain English explanations** of medical findings
- **Visual severity indicators** (green/yellow/red alerts)
- **Why you need treatment** explained simply
- **Cost breakdown** with insurance estimates
- **What to expect** during your hospital stay
- **Recovery timeline** and follow-up care

## 🧪 Testing

### Run the test system
```bash
python3 test_intelligent_system.py
```

### Test specific patient scenarios
```bash
python3 test_patients/test_runner.py
```

### Available test cases:
- Critical sepsis patient
- Young pneumonia case  
- Elderly with low oxygen
- Ambiguous chest pain

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/analyze` | POST | Upload files for analysis |
| `/patient-analysis` | POST | Generate patient view |
| `/patient` | GET | Patient-friendly results view |
| `/health` | GET | System health check |
| `/ws` | WebSocket | Real-time agent communication |

## 🔬 Medical Scoring Systems

The system implements validated clinical scores:

- **SIRS** - Systemic Inflammatory Response Syndrome
- **CURB-65** - Pneumonia severity score  
- **MEWS** - Modified Early Warning Score
- **qSOFA** - Quick sepsis screening

Each score uses evidence-based thresholds and provides actionable recommendations.

## 🚀 Advanced Features

### Blackboard System
- Event-driven architecture
- Pattern-based subscriptions
- Priority messaging (CRITICAL/HIGH/NORMAL/LOW)
- Question-answer protocols
- Opinion voting system

### Medical Intelligence
- Clinical pattern recognition
- Drug-drug interaction checking
- Kidney function calculations (eGFR)
- Antibiotic selection algorithms
- Critical value thresholds

### Fallback Mechanisms
- Works without AI models
- Template-based responses
- Mock data for demonstrations
- Graceful error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/NewAgent`)
3. Commit changes (`git commit -m 'Add CardiacAgent'`)
4. Push to branch (`git push origin feature/NewAgent`)
5. Open a Pull Request

### Adding New Agents

1. Create new file in `agents/`
2. Inherit from base agent pattern
3. Subscribe to relevant blackboard events
4. Implement medical logic
5. Add to orchestrator

## 📈 Performance

- Handles concurrent analyses
- Sub-second agent communication
- Asynchronous processing
- Minimal dependencies
- Works on standard hardware

## 🔒 Security Considerations

- No PHI storage (processes uploads in memory)
- Configurable for HIPAA compliance
- No external API calls required
- Local AI model support
- Audit trail of agent decisions

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Missing dependencies:**
```bash
pip3 install -r requirements.txt
```

**Agents not communicating:**
- Check console for WebSocket connection
- Ensure blackboard is initialized
- Verify agent subscriptions

## 📚 Documentation

- [Architecture Deep Dive](INTELLIGENT_SYSTEM_README.md)
- [Agent Communication](core/blackboard.py)
- [Medical Scoring](utils/medical_intelligence.py)
- [Running Instructions](RUN_INSTRUCTIONS.md)

## 🙏 Acknowledgments

- Clinical scoring systems from medical literature
- FastAPI for excellent web framework
- Medical professionals who inspired the agent behaviors

## 📝 License

This project is proprietary software. All rights reserved.

---

**Built with ❤️ to demonstrate how AI agents can collaborate like medical professionals**

*Note: This is a demonstration system. Not intended for actual medical use.*