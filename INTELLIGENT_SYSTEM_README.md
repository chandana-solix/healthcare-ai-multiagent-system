# Intelligent Healthcare Multi-Agent System

## 🚀 What's New

This enhanced version transforms the agents from simple rule-based systems into **intelligent medical specialists** that:

1. **Communicate and Debate**: Agents actively discuss findings with each other
2. **Use Medical Intelligence**: Real clinical scoring systems (SIRS, CURB-65, MEWS, qSOFA)
3. **Build Consensus**: Agents work together to reach agreement on diagnosis and treatment
4. **Apply Clinical Guidelines**: Evidence-based medicine with real treatment protocols

## 🏥 Key Improvements

### 1. Enhanced Blackboard System (`core/blackboard.py`)
- Real publish-subscribe pattern for agent communication
- Message types: FINDING, QUESTION, RESPONSE, ALERT, CONSENSUS
- Priority levels for critical alerts
- Conversation logging and tracking

### 2. Medical Intelligence (`utils/medical_intelligence.py`)
- **Clinical Scoring Systems**:
  - SIRS (Systemic Inflammatory Response Syndrome)
  - CURB-65 (Pneumonia severity)
  - MEWS (Modified Early Warning Score)
  - qSOFA (Quick SOFA for sepsis)
- **Pattern Recognition**:
  - Infection patterns (bacterial vs viral)
  - Cardiac patterns (heart failure, MI)
  - Sepsis risk assessment
- **Treatment Recommendations**:
  - Evidence-based antibiotic selection
  - Dosing adjustments for kidney function
  - Allergy considerations

### 3. Intelligent Agents

#### Lab Analyzer (`agents/intelligent_lab_analyzer.py`)
- Analyzes lab values with clinical context
- Identifies critical values and patterns
- Correlates with imaging findings
- Asks questions to other agents

#### Image Analyzer (`agents/intelligent_image_analyzer.py`)
- Reviews X-rays with awareness of lab findings
- Focuses search based on clinical suspicion
- Provides confidence scores
- Seeks consensus on findings

#### Risk Stratifier (`agents/intelligent_risk_stratification.py`)
- Calculates multiple validated risk scores
- Considers age, comorbidities, and findings
- Determines disposition (ICU vs floor vs discharge)
- Debates when findings conflict

#### Clinical Decision Maker (`agents/intelligent_clinical_decision.py`)
- Synthesizes all findings
- Creates evidence-based treatment plans
- Selects appropriate antibiotics
- Monitors for consensus

#### Consensus Builder (`agents/intelligent_consensus_builder.py`)
- Facilitates agreement among agents
- Resolves disagreements through discussion
- Creates unified action plans
- Ensures safety-first approach

## 🔧 How Agents Communicate

```python
# Example agent conversation:

LabAnalyzer: "🚨 CRITICAL WBC: 18.5, CRP: 125 - severe bacterial infection suspected"
ImageAnalyzer: "📌 Lab found infection - focusing on pneumonia... Found consolidation in RLL"
RiskAnalyst: "⚠️ Patient meets SIRS criteria, CURB-65 score 3/5 - high mortality risk"
LabAnalyzer: "✅ Imaging findings STRONGLY correlate with bacterial pneumonia"
DecisionMaker: "🏥 Consensus: Bacterial pneumonia with sepsis. Start ceftriaxone + azithromycin"
ConsensusBuilder: "🤝 All agents agree: Admit to stepdown unit with IV antibiotics"
```

## 🚀 Running the System

### Option 1: Web Interface
```bash
python intelligent_orchestrator.py
# Open http://localhost:8000
```

### Option 2: Test Script
```bash
python test_intelligent_system.py
```

## 📊 Example Output

When analyzing a patient with pneumonia and sepsis:

**Consensus Reached:**
- Primary Diagnosis: Bacterial pneumonia with severe sepsis
- Confidence: HIGH - Strong consensus
- Disposition: Admit to step-down/telemetry unit

**Action Plan:**
- Immediate: Blood cultures, start antibiotics within 1 hour
- Within 1 hour: 30mL/kg fluid bolus, lactate level
- Monitoring: Vital signs q2h, continuous pulse ox
- Antibiotics: Ceftriaxone 1g IV daily + Azithromycin 500mg IV daily

**Agent Communication:**
- Total Messages: 47
- Critical Alerts: 3
- Questions Asked: 5
- Consensus Topics: 4

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Lab Analyzer  │────▶│   Blackboard    │◀────│ Image Analyzer  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       ▲                         │
         │                       │                         │
         ▼                       │                         ▼
┌─────────────────┐              │              ┌─────────────────┐
│ Risk Stratifier │──────────────┴──────────────│ Decision Maker  │
└─────────────────┘                             └─────────────────┘
         │                                                 │
         └─────────────────┐         ┌─────────────────────┘
                           ▼         ▼
                    ┌─────────────────────┐
                    │ Consensus Builder   │
                    └─────────────────────┘
```

## 🔑 Key Features

1. **Real Medical Intelligence**: Uses validated clinical scoring systems
2. **Agent Communication**: Agents ask questions and respond to each other
3. **Consensus Building**: Multiple agents must agree on critical decisions
4. **Safety First**: When agents disagree, defaults to safer option
5. **Evidence-Based**: All recommendations based on clinical guidelines
6. **Transparency**: Full conversation log shows how decisions were made

## 📝 Requirements

- Python 3.8+
- FastAPI
- Original AI models (TorchXRayVision, EasyOCR) if available
- See requirements.txt for full list

## 🎯 Future Enhancements

1. Natural Language Processing for better agent communication
2. Learning from past cases
3. Integration with hospital systems
4. More specialized agents (Pharmacist, Radiologist subspecialists)
5. Real-time monitoring and adjustment

This intelligent system demonstrates how AI agents can work together like a real medical team, communicating and building consensus to provide better patient care.
