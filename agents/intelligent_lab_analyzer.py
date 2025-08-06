"""
Intelligent Lab Analyzer Agent that communicates and uses medical reasoning
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import our new modules
import sys
sys.path.append('..')
from core.blackboard import blackboard, MessageType, Priority
from utils.medical_intelligence import MedicalIntelligence, ClinicalPatterns

class IntelligentLabAnalyzerAgent:
    """
    Lab Analyzer that actually thinks and communicates
    """
    
    def __init__(self):
        self.agent_id = "LabAnalyzer"
        self.name = "Dr. LabTech"
        
        # Subscribe to relevant events
        blackboard.subscribe(
            self.agent_id,
            ["patient_data", "xray_*", "question_*"],
            self.handle_event
        )
        
        # Medical knowledge
        self.medical_intel = MedicalIntelligence()
        self.patterns = ClinicalPatterns()
    
    async def analyze(self, lab_values: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyze lab values with medical intelligence
        """
        print(f"\n[{self.name}] 🔬 Starting comprehensive lab analysis...")
        
        # Initialize findings
        findings = {
            'critical_findings': [],
            'abnormal_values': [],
            'patterns_identified': [],
            'clinical_correlations': [],
            'recommendations': []
        }
        
        # 1. Check each lab value intelligently
        await self._analyze_individual_values(lab_values, findings)
        
        # 2. Look for patterns
        await self._identify_clinical_patterns(lab_values, findings)
        
        # 3. Correlate with other findings if available
        await self._correlate_with_other_data(findings)
        
        # 4. Post findings to blackboard for other agents
        await self._communicate_findings(findings, lab_values)
        
        # 5. Ask questions if needed
        await self._ask_clarifying_questions(findings)
        
        return findings
    
    async def _analyze_individual_values(self, lab_values: Dict, findings: Dict):
        """
        Analyze each lab value with clinical context
        """
        critical_ranges = {
            'potassium': {'low': 2.5, 'high': 6.5, 'critical_low': 2.0, 'critical_high': 7.0},
            'sodium': {'low': 120, 'high': 160},
            'glucose': {'low': 40, 'high': 500},
            'creatinine': {'high': 3.0},
            'wbc': {'low': 2.0, 'high': 20.0},
            'hemoglobin': {'low': 7.0},
            'platelets': {'low': 20, 'high': 1000},
            'inr': {'high': 5.0},
            'lactate': {'high': 4.0},
            'troponin': {'high': 0.04},
            'bnp': {'high': 900},
            'crp': {'high': 100},
            'procalcitonin': {'high': 2.0}
        }
        
        for test, value in lab_values.items():
            if value is None or test not in critical_ranges:
                continue
            
            ranges = critical_ranges[test]
            
            # Check critical values
            if 'critical_high' in ranges and value > ranges['critical_high']:
                finding = f"CRITICAL {test.upper()}: {value} (life-threatening high)"
                findings['critical_findings'].append(finding)
                
                # Post critical alert
                await blackboard.post(
                    self.agent_id,
                    MessageType.ALERT,
                    f"critical_{test}",
                    {'test': test, 'value': value, 'severity': 'CRITICAL'},
                    Priority.CRITICAL
                )
                
            elif 'critical_low' in ranges and value < ranges.get('critical_low', 0):
                finding = f"CRITICAL {test.upper()}: {value} (life-threatening low)"
                findings['critical_findings'].append(finding)
                
                await blackboard.post(
                    self.agent_id,
                    MessageType.ALERT,
                    f"critical_{test}",
                    {'test': test, 'value': value, 'severity': 'CRITICAL'},
                    Priority.CRITICAL
                )
            
            # Check abnormal values
            elif 'high' in ranges and value > ranges['high']:
                finding = f"{test.upper()} elevated: {value}"
                findings['abnormal_values'].append(finding)
                
            elif 'low' in ranges and value < ranges['low']:
                finding = f"{test.upper()} low: {value}"
                findings['abnormal_values'].append(finding)
    
    async def _identify_clinical_patterns(self, lab_values: Dict, findings: Dict):
        """
        Look for clinical patterns in the labs
        """
        # Check for infection pattern
        vitals = blackboard.get_latest_finding('patient_vitals') or {}
        infection_pattern = self.patterns.identify_infection_pattern(lab_values, vitals)
        
        if infection_pattern:
            findings['patterns_identified'].append(infection_pattern)
            
            # Communicate the pattern
            if infection_pattern == "SEVERE_BACTERIAL_INFECTION":
                await blackboard.post(
                    self.agent_id,
                    MessageType.FINDING,
                    "severe_infection_detected",
                    {
                        'pattern': infection_pattern,
                        'evidence': f"WBC: {lab_values.get('wbc')}, CRP: {lab_values.get('crp')}",
                        'recommendation': "Start empiric antibiotics IMMEDIATELY"
                    },
                    Priority.HIGH
                )
            
            elif infection_pattern == "SEPSIS_PATTERN":
                await blackboard.post(
                    self.agent_id,
                    MessageType.ALERT,
                    "sepsis_suspected",
                    {
                        'lactate': lab_values.get('lactate'),
                        'wbc': lab_values.get('wbc'),
                        'action': "INITIATE SEPSIS PROTOCOL"
                    },
                    Priority.CRITICAL
                )
        
        # Check for cardiac pattern
        cardiac_pattern = self.patterns.identify_cardiac_pattern(lab_values, vitals)
        if cardiac_pattern:
            findings['patterns_identified'].append(cardiac_pattern)
            
            await blackboard.post(
                self.agent_id,
                MessageType.FINDING,
                "cardiac_issue_detected",
                {
                    'pattern': cardiac_pattern,
                    'bnp': lab_values.get('bnp'),
                    'troponin': lab_values.get('troponin')
                },
                Priority.HIGH
            )
        
        # Check for kidney dysfunction
        creatinine = lab_values.get('creatinine')
        if creatinine and creatinine > 1.5:
            egfr = self._calculate_egfr(creatinine, 
                                       blackboard.get_latest_finding('patient_age') or 50,
                                       blackboard.get_latest_finding('patient_gender') or 'M')
            
            findings['patterns_identified'].append(f"KIDNEY_DYSFUNCTION (eGFR: {egfr})")
            
            await blackboard.post(
                self.agent_id,
                MessageType.FINDING,
                "kidney_dysfunction",
                {
                    'creatinine': creatinine,
                    'egfr': egfr,
                    'stage': self._get_ckd_stage(egfr),
                    'impact': "Adjust medication dosing"
                },
                Priority.HIGH
            )
    
    async def _correlate_with_other_data(self, findings: Dict):
        """
        Correlate lab findings with other agent findings
        """
        # Check if imaging found anything
        xray_findings = blackboard.get_latest_finding('xray_analysis')
        
        if xray_findings and 'pneumonia' in str(xray_findings).lower():
            # We have pneumonia on X-ray, check inflammatory markers
            wbc = blackboard.get_latest_finding('lab_wbc')
            crp = blackboard.get_latest_finding('lab_crp')
            
            if wbc and wbc > 15 and crp and crp > 50:
                correlation = "Lab findings STRONGLY support bacterial pneumonia diagnosis"
                findings['clinical_correlations'].append(correlation)
                
                # Tell other agents
                await blackboard.post(
                    self.agent_id,
                    MessageType.FINDING,
                    "pneumonia_confirmed_by_labs",
                    {
                        'confidence': 'HIGH',
                        'evidence': f"WBC {wbc}, CRP {crp} with imaging findings",
                        'type': 'Bacterial pneumonia'
                    },
                    Priority.HIGH
                )
            else:
                correlation = "Lab findings suggest possible viral pneumonia (normal WBC/CRP)"
                findings['clinical_correlations'].append(correlation)
    
    async def _communicate_findings(self, findings: Dict, lab_values: Dict):
        """
        Communicate key findings to other agents
        """
        # Post lab summary
        summary = {
            'total_tests': len(lab_values),
            'critical_count': len(findings['critical_findings']),
            'abnormal_count': len(findings['abnormal_values']),
            'patterns': findings['patterns_identified'],
            'key_values': {k: v for k, v in lab_values.items() 
                          if k in ['wbc', 'crp', 'creatinine', 'bnp', 'troponin', 'lactate']}
        }
        
        await blackboard.post(
            self.agent_id,
            MessageType.FINDING,
            "lab_analysis_complete",
            summary,
            Priority.NORMAL
        )
        
        # If critical findings, ensure everyone knows
        if findings['critical_findings']:
            print(f"[{self.name}] 🚨 CRITICAL findings detected! Alerting all agents...")
            
            for critical in findings['critical_findings']:
                await blackboard.post(
                    self.agent_id,
                    MessageType.ALERT,
                    "critical_lab_alert",
                    {'finding': critical, 'action_required': True},
                    Priority.CRITICAL
                )
    
    async def _ask_clarifying_questions(self, findings: Dict):
        """
        Ask other agents questions based on findings
        """
        # If we found infection markers, ask imaging about pneumonia
        if any('INFECTION' in p for p in findings['patterns_identified']):
            await blackboard.ask_question(
                self.agent_id,
                "ImageAnalyzer, given the elevated infection markers (WBC, CRP), do you see any signs of pneumonia or other infection sources on imaging?",
                target_agents=['ImageAnalyzer']
            )
        
        # If kidney dysfunction, ask about medications
        if any('KIDNEY' in p for p in findings['patterns_identified']):
            await blackboard.ask_question(
                self.agent_id,
                "ClinicalDecision agent, patient has kidney dysfunction. Should we adjust antibiotic dosing?",
                target_agents=['ClinicalDecision']
            )
    
    async def handle_event(self, topic: str, message: Dict):
        """
        Handle events from other agents
        """
        print(f"[{self.name}] Received event: {topic}")
        
        # Respond to questions
        if topic.startswith("question_") and self.agent_id in message.get('content', ''):
            await self._respond_to_question(topic, message)
        
        # React to X-ray findings
        elif topic.startswith("xray_") and "pneumonia" in str(message.get('content', '')).lower():
            print(f"[{self.name}] X-ray shows pneumonia - let me check inflammatory markers...")
            # Re-evaluate labs in context of pneumonia
            
    async def _respond_to_question(self, question_id: str, message: Dict):
        """
        Respond to questions from other agents
        """
        question = message.get('content', '')
        
        if "kidney" in question.lower() and "dosing" in question.lower():
            response = "Yes, with the current kidney function, we should reduce antibiotic doses by 50% and avoid nephrotoxic medications."
            await blackboard.respond_to_question(self.agent_id, question_id, response)
    
    def _calculate_egfr(self, creatinine: float, age: int, gender: str) -> float:
        """
        Calculate estimated GFR using CKD-EPI equation (simplified)
        """
        # Simplified calculation
        if gender.upper() == 'F':
            egfr = 144 * (creatinine / 0.7) ** -0.329 * 0.993 ** age
        else:
            egfr = 141 * (creatinine / 0.9) ** -0.411 * 0.993 ** age
        
        return round(egfr, 1)
    
    def _get_ckd_stage(self, egfr: float) -> str:
        """
        Get CKD stage from eGFR
        """
        if egfr >= 90:
            return "Stage 1 (normal)"
        elif egfr >= 60:
            return "Stage 2 (mild)"
        elif egfr >= 45:
            return "Stage 3a (moderate)"
        elif egfr >= 30:
            return "Stage 3b (moderate)"
        elif egfr >= 15:
            return "Stage 4 (severe)"
        else:
            return "Stage 5 (kidney failure)"

# Create the intelligent agent
lab_analyzer = IntelligentLabAnalyzerAgent()
