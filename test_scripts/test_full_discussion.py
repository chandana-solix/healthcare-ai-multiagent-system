#!/usr/bin/env python3
"""
Test script to verify full discussion display
"""
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create test data with full conversation
test_data = {
    "patient": {
        "patient_id": "TEST001",
        "age": 65,
        "gender": "M",
        "chief_complaint": "Chest pain and difficulty breathing"
    },
    "consensus": {
        "primary_diagnosis": "Community-acquired pneumonia with sepsis",
        "disposition": "Admit to ICU"
    },
    "agent_communication": {
        "total_messages": 25,
        "critical_alerts": 3,
        "questions_asked": 5,
        "consensus_topics": 4
    },
    "conversation_highlights": [
        "🚨 RiskStratifier: Critical sepsis risk - qSOFA score 3/3, requires immediate ICU admission",
        "❓ LabAnalyzer asked: ImageAnalyzer, given the elevated infection markers (WBC, CRP), do you see any signs of pneumonia or other infection sources on imaging?",
        "❓ ClinicalDecision asked: LabAnalyzer, patient has kidney dysfunction. Should we adjust antibiotic dosing?",
        "🤝 Consensus reached on immediate ICU admission",
        "🤝 Consensus reached on broad-spectrum antibiotics with renal dosing",
        "❓ RiskStratifier asked: Has anyone considered the possibility of underlying malignancy given the rapid deterioration?",
        "🚨 LabAnalyzer: Severe metabolic acidosis detected - pH 7.25, lactate 4.2",
        "🤝 Consensus reached on fluid resuscitation protocol"
    ],
    "raw_conversation": [
        {
            "timestamp": "2025-01-15T10:32:15",
            "agent_id": "LabAnalyzer",
            "type": "finding",
            "content": "Initial lab analysis complete. WBC 18.5 (elevated), CRP 125 (significantly elevated), Procalcitonin 3.2 (high). Strong indicators of bacterial infection.",
            "topic": "lab_analysis_complete",
            "priority": 0
        },
        {
            "timestamp": "2025-01-15T10:32:18",
            "agent_id": "ImageAnalyzer",
            "type": "finding",
            "content": "Chest X-ray shows consolidation in right lower lobe consistent with pneumonia. No pleural effusion noted.",
            "topic": "xray_analysis_complete",
            "priority": 0
        },
        {
            "timestamp": "2025-01-15T10:32:20",
            "agent_id": "RiskStratifier",
            "type": "alert",
            "content": "Critical sepsis risk - qSOFA score 3/3 (altered mental status, RR 26, BP 85/50), requires immediate ICU admission",
            "topic": "sepsis_confirmed",
            "priority": 1
        },
        {
            "timestamp": "2025-01-15T10:32:22",
            "agent_id": "LabAnalyzer",
            "type": "question",
            "content": "ImageAnalyzer, given the elevated infection markers (WBC, CRP), do you see any signs of pneumonia or other infection sources on imaging?",
            "topic": "infection_source_query",
            "priority": 0
        },
        {
            "timestamp": "2025-01-15T10:32:24",
            "agent_id": "ImageAnalyzer",
            "type": "response",
            "content": "Yes, clear consolidation in right lower lobe. Pattern is classic for bacterial pneumonia. This correlates well with your lab findings.",
            "topic": "infection_source_confirmed",
            "priority": 0
        },
        {
            "timestamp": "2025-01-15T10:32:26",
            "agent_id": "ClinicalDecision",
            "type": "question",
            "content": "LabAnalyzer, patient has kidney dysfunction (Cr 1.8). Should we adjust antibiotic dosing?",
            "topic": "renal_dosing_query",
            "priority": 0
        },
        {
            "timestamp": "2025-01-15T10:32:28",
            "agent_id": "LabAnalyzer",
            "type": "response",
            "content": "Absolutely. With Cr 1.8 and BUN 35, we need renal dosing. Recommend reducing dose by 50% and monitoring levels.",
            "topic": "renal_dosing_confirmed",
            "priority": 0
        },
        {
            "timestamp": "2025-01-15T10:32:30",
            "agent_id": "ConsensusBuilder",
            "type": "consensus",
            "content": "All agents agree: Immediate ICU admission required for sepsis management",
            "topic": "immediate ICU admission",
            "priority": 0
        },
        {
            "timestamp": "2025-01-15T10:32:32",
            "agent_id": "ConsensusBuilder",
            "type": "consensus",
            "content": "Treatment consensus: Broad-spectrum antibiotics (Piperacillin-Tazobactam + Vancomycin) with renal dose adjustment",
            "topic": "broad-spectrum antibiotics with renal dosing",
            "priority": 0
        },
        {
            "timestamp": "2025-01-15T10:32:34",
            "agent_id": "RiskStratifier",
            "type": "question",
            "content": "Has anyone considered the possibility of underlying malignancy given the rapid deterioration?",
            "topic": "malignancy_consideration",
            "priority": 0
        },
        {
            "timestamp": "2025-01-15T10:32:36",
            "agent_id": "ImageAnalyzer",
            "type": "response",
            "content": "Good point. No obvious masses on current imaging, but CT chest might be warranted after stabilization.",
            "topic": "malignancy_follow_up",
            "priority": 0
        },
        {
            "timestamp": "2025-01-15T10:32:38",
            "agent_id": "LabAnalyzer",
            "type": "alert",
            "content": "Severe metabolic acidosis detected - pH 7.25, lactate 4.2",
            "topic": "metabolic_acidosis",
            "priority": 1
        },
        {
            "timestamp": "2025-01-15T10:32:40",
            "agent_id": "ClinicalDecision",
            "type": "finding",
            "content": "Initiating sepsis bundle: IV fluids 30mL/kg, blood cultures before antibiotics, lactate monitoring q2h",
            "topic": "sepsis_bundle_initiated",
            "priority": 0
        },
        {
            "timestamp": "2025-01-15T10:32:42",
            "agent_id": "ConsensusBuilder",
            "type": "consensus",
            "content": "Fluid resuscitation protocol agreed: 30mL/kg crystalloid bolus over 1 hour with reassessment",
            "topic": "fluid resuscitation protocol",
            "priority": 0
        }
    ]
}

# Save test data
with open('test_full_discussion_data.json', 'w') as f:
    json.dump(test_data, f, indent=2)

print("✅ Test data created successfully!")
print("📝 Test data includes:")
print(f"   - {len(test_data['raw_conversation'])} full conversation messages")
print(f"   - {len(test_data['conversation_highlights'])} conversation highlights")
print(f"   - {test_data['agent_communication']['total_messages']} total messages")
print(f"   - {test_data['agent_communication']['questions_asked']} questions asked")
print(f"   - {test_data['agent_communication']['critical_alerts']} critical alerts")
print("\n🚀 To test:")
print("1. Start the server: python intelligent_orchestrator.py")
print("2. Go to patient view: http://localhost:8000/patient")
print("3. Click on 'Medical Team Discussion' tab")
print("4. Click 'Show Full Discussion' to see complete conversation")
