"""
Intelligent Risk Stratification Agent that uses multiple scoring systems
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

import sys
sys.path.append('..')
from core.blackboard import blackboard, MessageType, Priority
from utils.medical_intelligence import MedicalIntelligence, RiskLevel, ClinicalScore

class IntelligentRiskStratificationAgent:
    """
    Risk assessment agent that uses real medical scoring and debates with other agents
    """
    
    def __init__(self):
        self.agent_id = "RiskStratifier"
        self.name = "Dr. RiskAnalyst"
        
        # Subscribe to all major findings
        blackboard.subscribe(
            self.agent_id,
            ["lab_analysis_complete", "xray_analysis_complete", 
             "pneumonia_confirmed_*", "sepsis_suspected", "critical_*",
             "patient_data", "question_*"],
            self.handle_event
        )
        
        self.medical_intel = MedicalIntelligence()
        self.patient_data = {}
        self.risk_factors = []
        
    async def analyze(self, patient_data: Dict) -> Dict[str, Any]:
        """
        Comprehensive risk assessment using multiple validated scores
        """
        print(f"\n[{self.name}] ⚡ Starting comprehensive risk stratification...")
        
        self.patient_data = patient_data
        vitals = patient_data.get('vitals', {})
        
        # Clear risk factors for each patient - FIX THE ACCUMULATION BUG
        self.risk_factors = []
        
        # Get lab data from blackboard
        lab_summary = blackboard.get_latest_finding('lab_analysis_complete') or {}
        lab_values = lab_summary.get('key_values', {})
        
        # Initialize risk assessment
        risk_assessment = {
            'clinical_scores': {},
            'overall_risk': RiskLevel.LOW,
            'risk_factors': [],
            'recommendations': [],
            'disposition': '',
            'monitoring_level': ''
        }
        
        # 1. Calculate all relevant clinical scores
        await self._calculate_clinical_scores(patient_data, vitals, lab_values, risk_assessment)
        
        # 2. Consider agent findings
        await self._incorporate_agent_findings(risk_assessment)
        
        # 3. Calculate overall risk
        self._determine_overall_risk(risk_assessment)
        
        # 4. Make recommendations
        self._generate_recommendations(risk_assessment)
        
        # 5. Communicate with other agents
        await self._communicate_risk_assessment(risk_assessment)
        
        # 6. Debate if there are conflicting findings
        await self._debate_risk_level(risk_assessment)
        
        return risk_assessment
    
    async def _calculate_clinical_scores(self, patient_data: Dict, vitals: Dict, 
                                       lab_values: Dict, risk_assessment: Dict):
        """
        Calculate all relevant medical scores
        """
        # SIRS Score
        sirs = self.medical_intel.calculate_sirs(vitals, lab_values)
        risk_assessment['clinical_scores']['SIRS'] = sirs
        
        if sirs.score >= 2:
            self.risk_factors.append(f"SIRS positive (score: {sirs.score}/4)")
            print(f"[{self.name}] ⚠️ Patient meets SIRS criteria - checking for sepsis")
        
        # qSOFA Score
        qsofa = self.medical_intel.calculate_qsofa(vitals)
        risk_assessment['clinical_scores']['qSOFA'] = qsofa
        
        if qsofa.score >= 2:
            self.risk_factors.append(f"qSOFA positive (score: {qsofa.score}/3)")
            print(f"[{self.name}] 🚨 High qSOFA score - high mortality risk!")
        
        # MEWS Score
        mews = self.medical_intel.calculate_mews(vitals)
        risk_assessment['clinical_scores']['MEWS'] = mews
        
        if mews.score >= 5:
            self.risk_factors.append(f"MEWS critical (score: {mews.score}/14)")
            print(f"[{self.name}] 🚨 MEWS indicates high risk of deterioration")
        
        # CURB-65 if pneumonia suspected
        if blackboard.has_alert('pneumonia_confirmed_on_imaging'):
            curb65 = self.medical_intel.calculate_curb65(patient_data, vitals, lab_values)
            risk_assessment['clinical_scores']['CURB-65'] = curb65
            
            if curb65.score >= 3:
                self.risk_factors.append(f"CURB-65 high risk (score: {curb65.score}/5)")
                print(f"[{self.name}] ⚠️ CURB-65 suggests high mortality risk from pneumonia")
        
        # Sepsis assessment
        if sirs.score >= 2 or qsofa.score >= 2:
            sepsis_risk = self.medical_intel.assess_sepsis_risk(sirs, qsofa, lab_values)
            risk_assessment['sepsis_assessment'] = sepsis_risk
            
            if 'SEVERE' in sepsis_risk['risk'] or 'SEPTIC' in sepsis_risk['risk']:
                print(f"[{self.name}] 🚨🚨🚨 SEPSIS/SEPTIC SHOCK LIKELY!")
                
                # Critical alert
                await blackboard.post(
                    self.agent_id,
                    MessageType.ALERT,
                    "sepsis_confirmed",
                    {
                        'severity': sepsis_risk['risk'],
                        'action': sepsis_risk['action'],
                        'evidence': sepsis_risk['factors']
                    },
                    Priority.CRITICAL
                )
    
    async def _incorporate_agent_findings(self, risk_assessment: Dict):
        """
        Consider findings from other agents
        """
        # Check for critical lab values
        critical_labs = blackboard.get_knowledge('critical_lab_alert')
        if critical_labs:
            for alert in critical_labs:
                self.risk_factors.append(f"Critical lab: {alert['content']['finding']}")
        
        # Check imaging findings
        xray_complete = blackboard.get_latest_finding('xray_analysis_complete')
        if xray_complete:
            impression = xray_complete.get('impression', '')
            if 'pneumonia' in impression.lower():
                self.risk_factors.append("Pneumonia confirmed on imaging")
            if 'bilateral' in str(xray_complete.get('key_findings', [])).lower():
                self.risk_factors.append("Bilateral lung involvement - higher severity")
        
        # Age-based risk
        age = self.patient_data.get('age', 0)
        if age >= 80:
            self.risk_factors.append(f"Very elderly patient ({age} years)")
        elif age >= 65:
            self.risk_factors.append(f"Elderly patient ({age} years)")
        
        # Comorbidities
        medical_history = self.patient_data.get('medical_history', {})
        chronic_conditions = medical_history.get('chronic_conditions', [])
        
        high_risk_conditions = ['diabetes', 'heart failure', 'copd', 'kidney disease', 'immunosuppression']
        for condition in chronic_conditions:
            if any(risk in condition.lower() for risk in high_risk_conditions):
                self.risk_factors.append(f"Comorbidity: {condition}")
        
        risk_assessment['risk_factors'] = self.risk_factors
    
    def _determine_overall_risk(self, risk_assessment: Dict):
        """
        Determine overall risk level from all factors
        """
        # First check for CRITICAL lab values
        lab_summary = blackboard.get_latest_finding('lab_analysis_complete') or {}
        lab_values = lab_summary.get('key_values', {})
        crp = lab_values.get('crp', 0)
        wbc = lab_values.get('wbc', 0)
        lactate = lab_values.get('lactate', 0)
        
        # CRITICAL if extreme lab values
        if crp and crp > 500:
            risk_assessment['overall_risk'] = RiskLevel.CRITICAL
            self.risk_factors.append(f'CRITICAL: Extreme CRP ({crp})')
            print(f"[{self.name}] 🚨🚨🚨 CRITICAL: CRP {crp} indicates severe infection/inflammation!")
            return
        
        # HIGH risk if very elevated inflammatory markers
        if (crp and crp > 200) or (wbc and wbc > 20) or (lactate and lactate > 4):
            risk_assessment['overall_risk'] = RiskLevel.HIGH
            self.risk_factors.append(f'Severe inflammation (CRP: {crp}, WBC: {wbc})')
            print(f"[{self.name}] 🚨 HIGH RISK: Severe inflammatory response")
            return
        
        # MODERATE risk if significantly elevated markers
        if (crp and crp > 100) or (wbc and wbc > 15) or (lactate and lactate > 2):
            risk_assessment['overall_risk'] = RiskLevel.MODERATE
            self.risk_factors.append(f'Significant inflammation (CRP: {crp}, WBC: {wbc})')
            return
        
        # Count high-risk indicators
        critical_count = 0
        high_count = 0
        
        # Check clinical scores
        for score_name, score in risk_assessment['clinical_scores'].items():
            if score.risk_level == RiskLevel.CRITICAL:
                critical_count += 1
            elif score.risk_level == RiskLevel.HIGH:
                high_count += 1
        
        # Check for sepsis
        if 'sepsis_assessment' in risk_assessment:
            if 'SEVERE' in risk_assessment['sepsis_assessment']['risk']:
                critical_count += 2
        
        # Check critical labs
        if any('Critical lab' in factor for factor in self.risk_factors):
            critical_count += 1
        
        # Determine overall risk
        if critical_count >= 2:
            risk_assessment['overall_risk'] = RiskLevel.CRITICAL
        elif critical_count >= 1 or high_count >= 2:
            risk_assessment['overall_risk'] = RiskLevel.HIGH
        elif high_count >= 1 or len(self.risk_factors) >= 3:
            risk_assessment['overall_risk'] = RiskLevel.MODERATE
        else:
            risk_assessment['overall_risk'] = RiskLevel.LOW
        
        print(f"[{self.name}] Overall risk assessment: {risk_assessment['overall_risk'].value}")
    
    def _generate_recommendations(self, risk_assessment: Dict):
        """
        Generate risk-based recommendations
        """
        risk_level = risk_assessment['overall_risk']
        
        if risk_level == RiskLevel.CRITICAL:
            risk_assessment['disposition'] = "ICU admission required"
            risk_assessment['monitoring_level'] = "Continuous monitoring"
            risk_assessment['recommendations'] = [
                "IMMEDIATE ICU transfer",
                "Continuous cardiac and O2 monitoring",
                "Arterial line for BP monitoring",
                "Central line access",
                "Prepare for intubation if needed",
                "Initiate appropriate protocols (sepsis, ACS, etc.)",
                "Notify critical care team"
            ]
            
        elif risk_level == RiskLevel.HIGH:
            risk_assessment['disposition'] = "Admit to step-down/telemetry unit"
            risk_assessment['monitoring_level'] = "Enhanced monitoring"
            risk_assessment['recommendations'] = [
                "Admit to monitored bed",
                "Vital signs q2h",
                "Continuous pulse oximetry",
                "Daily labs",
                "Rapid response team awareness",
                "Consider ICU if deteriorates"
            ]
            
        elif risk_level == RiskLevel.MODERATE:
            risk_assessment['disposition'] = "Admit to medical floor"
            risk_assessment['monitoring_level'] = "Standard monitoring"
            risk_assessment['recommendations'] = [
                "Admit for observation",
                "Vital signs q4h",
                "Daily labs",
                "Monitor response to treatment",
                "Consider discharge in 24-48h if improving"
            ]
            
        else:  # LOW
            risk_assessment['disposition'] = "Consider discharge with close follow-up"
            risk_assessment['monitoring_level'] = "Outpatient"
            risk_assessment['recommendations'] = [
                "Discharge home if stable",
                "Primary care follow-up in 24-48 hours",
                "Return precautions given",
                "Home monitoring instructions",
                "Clear discharge criteria met"
            ]
    
    async def _communicate_risk_assessment(self, risk_assessment: Dict):
        """
        Share risk assessment with other agents
        """
        # Post comprehensive risk assessment
        summary = {
            'overall_risk': risk_assessment['overall_risk'].value,
            'risk_factors': self.risk_factors[:5],  # Top 5 factors
            'disposition': risk_assessment['disposition'],
            'key_scores': {
                name: {'score': score.score, 'max': score.max_score, 'risk': score.risk_level.value}
                for name, score in risk_assessment['clinical_scores'].items()
            }
        }
        
        await blackboard.post(
            self.agent_id,
            MessageType.FINDING,
            "risk_assessment_complete",
            summary,
            Priority.HIGH if risk_assessment['overall_risk'] in [RiskLevel.HIGH, RiskLevel.CRITICAL] else Priority.NORMAL
        )
        
        # Post opinion for consensus
        opinion = f"Risk level is {risk_assessment['overall_risk'].value}. "
        opinion += f"Recommend: {risk_assessment['disposition']}"
        
        blackboard.post_opinion(
            self.agent_id,
            "disposition_recommendation",
            opinion,
            confidence=0.85  # High confidence in validated scores
        )
        
        # Alert if critical
        if risk_assessment['overall_risk'] == RiskLevel.CRITICAL:
            print(f"[{self.name}] 🚨 CRITICAL RISK - Alerting all agents!")
            
            await blackboard.post(
                self.agent_id,
                MessageType.ALERT,
                "patient_critical",
                {
                    'risk_level': 'CRITICAL',
                    'immediate_action': risk_assessment['recommendations'][0],
                    'evidence': self.risk_factors[:3]
                },
                Priority.CRITICAL
            )
    
    async def _debate_risk_level(self, risk_assessment: Dict):
        """
        Debate risk level if there are conflicting findings
        """
        # Check if other agents disagree
        lab_patterns = blackboard.get_latest_finding('lab_analysis_complete')
        
        # Example: If labs show minor abnormalities but scores are high
        if lab_patterns and lab_patterns.get('critical_count', 0) == 0 and \
           risk_assessment['overall_risk'] in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            
            await blackboard.ask_question(
                self.agent_id,
                "My risk scores indicate HIGH/CRITICAL risk, but labs don't show critical values. "
                "Should we still proceed with aggressive management given the clinical scores?",
                target_agents=['LabAnalyzer', 'ClinicalDecision']
            )
        
        # If pneumonia but low risk scores
        if blackboard.has_alert('pneumonia_confirmed_on_imaging') and \
           risk_assessment['overall_risk'] == RiskLevel.LOW:
            
            print(f"[{self.name}] 🤔 Interesting - pneumonia confirmed but risk scores are low...")
            
            await blackboard.post(
                self.agent_id,
                MessageType.FINDING,
                "risk_paradox",
                {
                    'finding': "Pneumonia present but low risk scores",
                    'explanation': "Young patient with no comorbidities and stable vitals",
                    'recommendation': "Consider outpatient management with close follow-up"
                },
                Priority.NORMAL
            )
    
    async def handle_event(self, topic: str, message: Dict):
        """
        Handle events from other agents
        """
        # Store patient data
        if topic == "patient_data":
            self.patient_data = message.get('content', {})
            print(f"[{self.name}] Received patient data for {self.patient_data.get('name', 'Unknown')}")
        
        # React to critical findings
        elif topic.startswith("critical_"):
            print(f"[{self.name}] 🚨 Critical finding received - re-evaluating risk...")
            self.risk_factors.append(f"Critical alert: {topic}")
            
        # React to sepsis alert
        elif topic == "sepsis_suspected":
            print(f"[{self.name}] 🚨 SEPSIS SUSPECTED - Upgrading risk assessment!")
            
            await blackboard.post(
                self.agent_id,
                MessageType.RESPONSE,
                "sepsis_protocol_initiated",
                "Initiating sepsis bundle - labs, cultures, antibiotics, fluids",
                Priority.CRITICAL
            )
        
        # Respond to questions
        elif topic.startswith("question_") and self.agent_id in str(message.get('target_agents', [])):
            question = message.get('content', '')
            
            if "aggressive management" in question:
                response = "Yes, clinical scores have been validated to predict deterioration. "
                response += "Even with normal labs now, high scores indicate impending decompensation. "
                response += "Recommend proceeding with higher level of care."
                
                await blackboard.respond_to_question(self.agent_id, topic, response)

# Create the intelligent agent
risk_stratifier = IntelligentRiskStratificationAgent()
