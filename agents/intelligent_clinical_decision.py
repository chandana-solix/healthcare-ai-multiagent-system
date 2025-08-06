"""
Intelligent Clinical Decision Agent that makes evidence-based treatment decisions
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

import sys
sys.path.append('..')
from core.blackboard import blackboard, MessageType, Priority
from utils.medical_intelligence import MedicalIntelligence, RiskLevel

class IntelligentClinicalDecisionAgent:
    """
    Clinical decision maker that synthesizes all findings and debates treatment
    """
    
    def __init__(self):
        self.agent_id = "ClinicalDecision"
        self.name = "Dr. DecisionMaker"
        
        # Subscribe to all major findings and questions
        blackboard.subscribe(
            self.agent_id,
            ["risk_assessment_complete", "lab_analysis_complete", 
             "xray_analysis_complete", "pneumonia_confirmed_*",
             "sepsis_*", "patient_data", "question_*", "*_confirmed"],
            self.handle_event
        )
        
        self.medical_intel = MedicalIntelligence()
        self.patient_data = {}
        
    async def analyze(self) -> Dict[str, Any]:
        """
        Make clinical decisions based on all available evidence
        """
        print(f"\n[{self.name}] 🏥 Synthesizing all findings to make clinical decisions...")
        
        # Gather all evidence
        evidence = await self._gather_all_evidence()
        
        # Determine primary diagnosis
        diagnosis = await self._determine_diagnosis(evidence)
        
        # Create treatment plan
        treatment_plan = await self._create_treatment_plan(diagnosis, evidence)
        
        # Check for disagreements
        await self._check_agent_consensus(diagnosis, treatment_plan)
        
        # Communicate decisions
        await self._communicate_decisions(diagnosis, treatment_plan)
        
        # Ask for final confirmation
        await self._seek_final_consensus(treatment_plan)
        
        return {
            'diagnosis': diagnosis,
            'treatment_plan': treatment_plan,
            'evidence_based': True,
            'consensus_sought': True
        }
    
    async def _gather_all_evidence(self) -> Dict:
        """
        Gather all findings from other agents
        """
        evidence = {
            'patient_data': blackboard.get_latest_finding('patient_data') or {},
            'lab_analysis': blackboard.get_latest_finding('lab_analysis_complete') or {},
            'imaging': blackboard.get_latest_finding('xray_analysis_complete') or {},
            'risk_assessment': blackboard.get_latest_finding('risk_assessment_complete') or {},
            'critical_alerts': blackboard.active_alerts,
            'consensus_topics': blackboard.consensus_topics
        }
        
        # Print summary of evidence
        print(f"[{self.name}] Evidence gathered:")
        print(f"  - Lab patterns: {evidence['lab_analysis'].get('patterns', [])}")
        print(f"  - Imaging: {evidence['imaging'].get('impression', 'None')}")
        print(f"  - Risk level: {evidence['risk_assessment'].get('overall_risk', 'Unknown')}")
        print(f"  - Critical alerts: {len(evidence['critical_alerts'])}")
        
        return evidence
    
    async def _determine_diagnosis(self, evidence: Dict) -> Dict:
        """
        Determine primary and differential diagnoses
        """
        diagnosis = {
            'primary': 'Undifferentiated illness',
            'differential': [],
            'confidence': 0.5,
            'supporting_evidence': []
        }
        
        # Get patient info
        patient_data = evidence['patient_data']
        chief_complaint = patient_data.get('chief_complaint', '').lower()
        age = patient_data.get('age', 0)
        
        # Get oxygen saturation from vitals
        vitals = patient_data.get('vitals', {})
        o2_sat = vitals.get('oxygen_saturation', 100)
        
        # Get lab patterns
        lab_patterns = evidence['lab_analysis'].get('patterns', [])
        lab_values = evidence['lab_analysis'].get('key_values', {})
        crp = lab_values.get('crp', 0)
        wbc = lab_values.get('wbc', 0)
        
        # Get imaging findings
        imaging_impression = evidence['imaging'].get('impression', '').lower()
        imaging_findings = evidence['imaging'].get('key_findings', [])
        
        # Check for pneumonia - MULTIPLE ways to detect
        pneumonia_indicators = 0
        if 'pneumonia' in imaging_impression:
            pneumonia_indicators += 2
        if any('pneumonia' in str(finding).lower() for finding in imaging_findings):
            pneumonia_indicators += 2
        if any('infiltrat' in str(finding).lower() for finding in imaging_findings):
            pneumonia_indicators += 1
        if any('consolidation' in str(finding).lower() for finding in imaging_findings):
            pneumonia_indicators += 1
        if 'SEVERE_BACTERIAL_INFECTION' in lab_patterns and ('cough' in chief_complaint or 'fever' in chief_complaint):
            pneumonia_indicators += 2
        
        if pneumonia_indicators >= 2:
            if 'SEVERE_BACTERIAL_INFECTION' in lab_patterns:
                diagnosis['primary'] = "Bacterial pneumonia with severe sepsis"
                diagnosis['confidence'] = 0.9
                diagnosis['supporting_evidence'] = [
                    "Pneumonia on imaging",
                    "Elevated inflammatory markers",
                    "SIRS criteria met"
                ]
            else:
                diagnosis['primary'] = "Community-acquired pneumonia"
                diagnosis['confidence'] = 0.8
                diagnosis['supporting_evidence'] = [
                    "Pneumonia on imaging",
                    "Clinical presentation consistent"
                ]
            
            diagnosis['differential'] = [
                "Viral pneumonia",
                "Atypical pneumonia",
                "Aspiration pneumonia"
            ]
        
        # Check for chronic cough with high CRP
        elif 'chronic' in chief_complaint and 'cough' in chief_complaint:
            if crp and crp > 100:
                diagnosis['primary'] = "Chronic bronchitis with acute exacerbation"
                diagnosis['confidence'] = 0.7
                diagnosis['supporting_evidence'] = [
                    "Chronic cough history",
                    f"Markedly elevated CRP ({crp})",
                    "Normal chest X-ray"
                ]
                diagnosis['differential'] = [
                    "Occult pneumonia",
                    "Tuberculosis",
                    "Malignancy",
                    "Autoimmune process"
                ]
            elif 'INFLAMMATORY_PROCESS' in lab_patterns:
                diagnosis['primary'] = "Inflammatory respiratory condition"
                diagnosis['confidence'] = 0.6
                diagnosis['supporting_evidence'] = [
                    "Chronic symptoms",
                    "Elevated inflammatory markers",
                    "Requires further investigation"
                ]
                diagnosis['differential'] = [
                    "Chronic bronchitis",
                    "Asthma",
                    "Interstitial lung disease",
                    "Post-infectious cough"
                ]
            else:
                diagnosis['primary'] = "Chronic cough syndrome"
                diagnosis['confidence'] = 0.5
                diagnosis['supporting_evidence'] = [
                    "Persistent symptoms",
                    "No acute findings"
                ]
        
        # Check for sepsis
        elif any('sepsis' in str(alert.get('topic', '')).lower() for alert in evidence['critical_alerts']):
            diagnosis['primary'] = "Sepsis of unknown origin"
            diagnosis['confidence'] = 0.85
            diagnosis['supporting_evidence'] = [
                "SIRS criteria positive",
                "Organ dysfunction present",
                "Elevated lactate"
            ]
            diagnosis['differential'] = [
                "Urosepsis",
                "Pneumonia",
                "Intra-abdominal infection"
            ]
        
        # Check for heart failure
        elif 'HEART_FAILURE' in lab_patterns:
            diagnosis['primary'] = "Acute decompensated heart failure"
            diagnosis['confidence'] = 0.85
            diagnosis['supporting_evidence'] = [
                "Elevated BNP",
                "Cardiomegaly on imaging",
                "Clinical presentation"
            ]
            diagnosis['differential'] = [
                "Pulmonary embolism",
                "Pneumonia",
                "COPD exacerbation"
            ]
        
        # Check for heart failure by symptoms and imaging
        elif (('pillows' in chief_complaint or 'lie flat' in chief_complaint or 
               'orthopnea' in chief_complaint or 'breathing' in chief_complaint) and
              any('cardiomegaly' in str(finding).lower() for finding in imaging_findings)):
            diagnosis['primary'] = "Congestive heart failure with acute exacerbation"
            diagnosis['confidence'] = 0.75
            diagnosis['supporting_evidence'] = [
                "Orthopnea (needs pillows to sleep)",
                "Cardiomegaly on imaging",
                "Elevated BP"
            ]
            diagnosis['differential'] = [
                "Pulmonary edema",
                "COPD",
                "Sleep apnea"
            ]
        
        # Check for respiratory infection without clear pneumonia
        elif ('cough' in chief_complaint or 'breathing' in chief_complaint) and \
             ('BACTERIAL_INFECTION' in lab_patterns or crp > 50):
            if 'productive' in chief_complaint:
                diagnosis['primary'] = "Acute bronchitis"
            else:
                diagnosis['primary'] = "Lower respiratory tract infection"
            diagnosis['confidence'] = 0.7
            diagnosis['supporting_evidence'] = [
                "Respiratory symptoms",
                f"Elevated CRP ({crp})",
                "Bacterial pattern on labs"
            ]
        
        # Check for COPD/respiratory disease without infection
        elif ('breath' in chief_complaint or 'dyspnea' in chief_complaint or 
              'shortness' in chief_complaint) and o2_sat < 94:
            # Check for chronic vs acute
            if 'chronic' in chief_complaint:
                if patient_data.get('medical_history', {}).get('smoking') in ['Current', 'Former']:
                    diagnosis['primary'] = "COPD exacerbation"
                    diagnosis['confidence'] = 0.75
                    diagnosis['supporting_evidence'] = [
                        "Chronic dyspnea with acute worsening",
                        "Hypoxemia (O2 < 94%)",
                        "Smoking history"
                    ]
                else:
                    diagnosis['primary'] = "Chronic respiratory failure"
                    diagnosis['confidence'] = 0.65
                    diagnosis['supporting_evidence'] = [
                        "Chronic progressive dyspnea",
                        "Hypoxemia",
                        "No clear cardiac etiology"
                    ]
            else:
                diagnosis['primary'] = "Acute hypoxemic respiratory failure"
                diagnosis['confidence'] = 0.7
                diagnosis['supporting_evidence'] = [
                    "Acute dyspnea",
                    "Hypoxemia",
                    "Requires further evaluation"
                ]
            
            diagnosis['differential'] = [
                "Pulmonary embolism",
                "Pneumonia",
                "Heart failure",
                "Interstitial lung disease"
            ]
        
        return diagnosis
    
    async def _create_treatment_plan(self, diagnosis: Dict, evidence: Dict) -> Dict:
        """
        Create evidence-based treatment plan
        """
        plan = {
            'disposition': '',
            'immediate_interventions': [],
            'medications': [],
            'monitoring': [],
            'consultations': [],
            'follow_up': ''
        }
        
        # Get risk level
        risk_level = evidence['risk_assessment'].get('overall_risk', 'MODERATE')
        primary_dx = diagnosis['primary'].lower()
        confidence = diagnosis['confidence']
        
        # Determine disposition based on BOTH diagnosis AND risk
        # Don't just copy from risk assessment - make clinical decision
        if risk_level == 'CRITICAL' or 'sepsis' in primary_dx:
            plan['disposition'] = 'Admit to ICU'
        elif risk_level == 'HIGH':
            if 'pneumonia' in primary_dx and 'severe' in primary_dx:
                plan['disposition'] = 'Admit to step-down/telemetry unit'
            else:
                plan['disposition'] = 'Admit to medical floor'
        elif risk_level == 'MODERATE':
            # For moderate risk, admission depends on diagnosis
            if any(serious in primary_dx for serious in ['pneumonia', 'heart failure', 'sepsis', 'copd exacerbation']):
                plan['disposition'] = 'Admit to medical floor'
            elif 'respiratory failure' in primary_dx or 'hypoxemic' in primary_dx:
                plan['disposition'] = 'Admit for observation'
            elif confidence < 0.6 and 'undifferentiated' in primary_dx:
                # Unclear diagnosis with moderate risk - observe, don't admit
                plan['disposition'] = 'Observation unit for 24 hours'
            else:
                plan['disposition'] = 'Home with urgent care follow-up within 24 hours'
        else:  # LOW risk
            if 'exacerbation' in primary_dx:
                plan['disposition'] = 'Treat and release with medications, follow-up in 48 hours'
            else:
                plan['disposition'] = 'Home with primary care follow-up'
        
        # Diagnosis-specific treatment
        if 'pneumonia' in primary_dx:
            # Get antibiotic recommendations
            patient_data = evidence['patient_data']
            allergies = patient_data.get('medical_history', {}).get('allergies', [])
            
            # Check kidney function
            kidney_dysfunction = blackboard.get_latest_finding('kidney_dysfunction')
            gfr = kidney_dysfunction.get('egfr', 90) if kidney_dysfunction else 90
            
            # Get CRP value to assess severity
            crp = evidence['lab_analysis'].get('key_values', {}).get('crp', 0)
            
            # If CRP > 1000, this is SEVERE regardless of other factors
            if crp and crp > 1000:
                plan['disposition'] = 'Admit to ICU'
                plan['immediate_interventions'].insert(0, "STAT antibiotics within 1 hour")
                plan['immediate_interventions'].append("Sepsis bundle activation")
                print(f"[{self.name}] 🚨 CRP {crp} - Severe infection requiring ICU!")
            
            abx_recs = self.medical_intel.get_antibiotic_recommendations(
                'pneumonia', 
                allergies,
                gfr
            )
            
            plan['medications'].extend(abx_recs['antibiotics'])
            
            # Add supportive care
            plan['immediate_interventions'].extend([
                "Supplemental oxygen to maintain SpO2 > 92%",
                "IV access and fluids",
                "Blood cultures before antibiotics",
                "Respiratory isolation if COVID not ruled out"
            ])
            
            plan['monitoring'] = [
                "Continuous pulse oximetry",
                "Vital signs q4h",
                "Daily CBC, BMP",
                "Repeat CXR in 48h if not improving"
            ]
            
            if 'severe' in primary_dx or 'sepsis' in primary_dx:
                plan['immediate_interventions'].insert(0, "STAT antibiotics within 1 hour")
                plan['immediate_interventions'].append("Lactate level now and in 6 hours")
                plan['monitoring'][1] = "Vital signs q2h"
                plan['consultations'].append("Consider ICU consultation")
        
        elif 'sepsis' in primary_dx:
            plan['immediate_interventions'] = [
                "INITIATE SEPSIS BUNDLE IMMEDIATELY",
                "Blood cultures x2 from different sites",
                "Lactate level STAT",
                "Broad spectrum antibiotics within 1 hour",
                "30mL/kg crystalloid fluid bolus",
                "Monitor urine output"
            ]
            
            # Get antibiotic recommendations for unknown source
            patient_data = evidence['patient_data']
            allergies = patient_data.get('medical_history', {}).get('allergies', [])
            
            abx_recs = self.medical_intel.get_antibiotic_recommendations(
                'sepsis_unknown_source',
                allergies
            )
            
            plan['medications'].extend(abx_recs['antibiotics'])
            plan['consultations'].append("ICU consultation STAT")
            
        elif 'heart failure' in primary_dx:
            plan['medications'] = [
                "Furosemide 40mg IV BID",
                "Continue home cardiac medications"
            ]
            
            plan['immediate_interventions'] = [
                "Supplemental oxygen if needed",
                "Daily weights",
                "Fluid restriction 1.5L/day",
                "Low sodium diet"
            ]
            
            plan['monitoring'] = [
                "Strict I&O",
                "Daily BMP to monitor electrolytes",
                "BNP trend",
                "Telemetry monitoring"
            ]
            
            plan['consultations'].append("Cardiology consultation")
        
        # Follow-up based on disposition
        if "ICU" in plan['disposition']:
            plan['follow_up'] = "Continuous ICU management"
        elif "admit" in plan['disposition'].lower():
            plan['follow_up'] = "Daily attending rounds"
        else:
            plan['follow_up'] = "Primary care in 24-48 hours"
        
        return plan
    
    async def _check_agent_consensus(self, diagnosis: Dict, treatment_plan: Dict):
        """
        Check if other agents agree with our assessment
        """
        # Check consensus topics
        primary_dx_consensus = blackboard.consensus_topics.get('primary_diagnosis', {})
        
        if primary_dx_consensus:
            consensus_dx = primary_dx_consensus.get('consensus', '')
            our_dx = diagnosis['primary']
            
            if our_dx.lower() not in consensus_dx.lower():
                print(f"[{self.name}] 🤔 My diagnosis differs from consensus...")
                
                await blackboard.ask_question(
                    self.agent_id,
                    f"I'm diagnosing {our_dx}, but others suggest {consensus_dx}. "
                    f"Can we review the key findings that support each diagnosis?",
                    target_agents=['LabAnalyzer', 'ImageAnalyzer', 'RiskStratifier']
                )
    
    async def _communicate_decisions(self, diagnosis: Dict, treatment_plan: Dict):
        """
        Share clinical decisions with all agents
        """
        decision_summary = {
            'primary_diagnosis': diagnosis['primary'],
            'confidence': diagnosis['confidence'],
            'disposition': treatment_plan['disposition'],
            'immediate_actions': treatment_plan['immediate_interventions'][:3],
            'key_medications': treatment_plan['medications'][:2]
        }
        
        await blackboard.post(
            self.agent_id,
            MessageType.FINDING,
            "clinical_decision_complete",
            decision_summary,
            Priority.HIGH
        )
        
        # Post opinion for consensus
        opinion = f"Primary diagnosis: {diagnosis['primary'].replace('_', ' ')}. "
        opinion += f"Disposition: {treatment_plan['disposition']}. "
        opinion += f"Start {treatment_plan['medications'][0] if treatment_plan['medications'] else 'supportive care'}"
        
        blackboard.post_opinion(
            self.agent_id,
            "primary_diagnosis",
            diagnosis['primary'],
            confidence=diagnosis['confidence']
        )
        
        blackboard.post_opinion(
            self.agent_id,
            "treatment_plan",
            opinion,
            confidence=diagnosis['confidence']
        )
        
        # If critical patient, ensure everyone knows the plan
        if any('CRITICAL' in str(alert) for alert in blackboard.active_alerts):
            print(f"[{self.name}] 🚨 CRITICAL PATIENT - Broadcasting treatment plan!")
            
            await blackboard.post(
                self.agent_id,
                MessageType.ALERT,
                "critical_treatment_plan",
                {
                    'diagnosis': diagnosis['primary'],
                    'immediate_action': treatment_plan['immediate_interventions'][0],
                    'disposition': treatment_plan['disposition']
                },
                Priority.CRITICAL
            )
    
    async def _seek_final_consensus(self, treatment_plan: Dict):
        """
        Seek final agreement from all agents
        """
        await blackboard.ask_question(
            self.agent_id,
            f"Final treatment plan: {treatment_plan['disposition']} with "
            f"{treatment_plan['medications'][0] if treatment_plan['medications'] else 'supportive care'}. "
            f"Do all agents agree with this plan? Any concerns or modifications needed?",
            target_agents=['LabAnalyzer', 'ImageAnalyzer', 'RiskStratifier']
        )
    
    async def handle_event(self, topic: str, message: Dict):
        """
        Handle events from other agents
        """
        # Store patient data
        if topic == "patient_data":
            self.patient_data = message.get('content', {})
        
        # React to risk assessment
        elif topic == "risk_assessment_complete":
            risk_data = message.get('content', {})
            print(f"[{self.name}] Risk assessment received: {risk_data.get('overall_risk')}")
            
            # If critical risk, start planning immediately
            if risk_data.get('overall_risk') == 'CRITICAL':
                print(f"[{self.name}] 🚨 Critical patient - expediting treatment decisions!")
        
        # Respond to questions about treatment
        elif topic.startswith("question_") and self.agent_id in str(message.get('target_agents', [])):
            question = message.get('content', '')
            
            if "kidney" in question and "dosing" in question:
                response = "Absolutely correct. With kidney dysfunction, we must adjust doses:\n"
                response += "- Reduce beta-lactam antibiotics by 50%\n"
                response += "- Avoid NSAIDs completely\n"
                response += "- Monitor drug levels for vancomycin if used"
                
                await blackboard.respond_to_question(self.agent_id, topic, response)
            
            elif "additional tests" in question:
                response = "For pneumonia differential:\n"
                response += "- Respiratory viral panel\n"
                response += "- Legionella and pneumococcal antigens\n"
                response += "- Procalcitonin to guide antibiotic duration\n"
                response += "- Consider bronchoscopy if not improving"
                
                await blackboard.respond_to_question(self.agent_id, topic, response)

# Create the intelligent agent
clinical_decision_maker = IntelligentClinicalDecisionAgent()
