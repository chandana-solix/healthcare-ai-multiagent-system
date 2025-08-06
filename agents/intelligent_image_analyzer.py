"""
Intelligent Image Analyzer Agent that correlates with other findings
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

import sys
sys.path.append('..')
from core.blackboard import blackboard, MessageType, Priority
from utils.medical_intelligence import MedicalIntelligence

class IntelligentImageAnalyzerAgent:
    """
    Radiologist agent that actively correlates findings with other agents
    """
    
    def __init__(self):
        self.agent_id = "ImageAnalyzer"
        self.name = "Dr. Radiologist"
        
        # Subscribe to relevant events
        blackboard.subscribe(
            self.agent_id,
            ["severe_infection_detected", "cardiac_issue_detected", 
             "lab_analysis_complete", "question_*"],
            self.handle_event
        )
        
        self.medical_intel = MedicalIntelligence()
    
    async def analyze(self, xray_findings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze X-ray with context from other agents
        """
        print(f"\n[{self.name}] 🩻 Beginning chest X-ray analysis...")
        
        # Get context from other agents first
        context = await self._gather_clinical_context()
        
        # Enhanced analysis based on context
        enhanced_findings = await self._contextual_image_analysis(xray_findings, context)
        
        # Correlate with lab findings
        correlations = await self._correlate_with_labs(enhanced_findings)
        
        # Post findings for other agents
        await self._communicate_findings(enhanced_findings, correlations)
        
        # Build consensus with other agents
        await self._seek_consensus(enhanced_findings)
        
        return {
            'original_findings': xray_findings,
            'enhanced_analysis': enhanced_findings,
            'clinical_correlations': correlations,
            'consensus_building': True
        }
    
    async def _gather_clinical_context(self) -> Dict:
        """
        Gather relevant context from blackboard before analysis
        """
        context = {
            'infection_suspected': blackboard.has_alert('severe_infection_detected'),
            'cardiac_issue': blackboard.get_latest_finding('cardiac_issue_detected'),
            'lab_summary': blackboard.get_latest_finding('lab_analysis_complete'),
            'patient_symptoms': blackboard.get_latest_finding('chief_complaint')
        }
        
        if context['infection_suspected']:
            print(f"[{self.name}] 📌 Lab agent found infection markers - will look carefully for pneumonia")
        
        if context['cardiac_issue']:
            print(f"[{self.name}] 📌 Cardiac markers elevated - will assess for heart failure signs")
        
        return context
    
    async def _contextual_image_analysis(self, xray_findings: Dict, context: Dict) -> Dict:
        """
        Enhance image analysis based on clinical context
        """
        enhanced = {
            'primary_findings': [],
            'secondary_findings': [],
            'clinical_impression': '',
            'confidence': 0.0,
            'differential_diagnosis': [],
            'follow_up_needed': []
        }
        
        # Extract AI predictions if available
        ai_predictions = xray_findings.get('ai_predictions', {})
        
        # If infection is suspected, focus on infection patterns
        if context['infection_suspected']:
            # Look specifically for pneumonia patterns
            pneumonia_prob = ai_predictions.get('Pneumonia', 0)
            infiltration_prob = ai_predictions.get('Infiltration', 0)
            consolidation_prob = ai_predictions.get('Consolidation', 0)
            
            if pneumonia_prob > 0.7 or consolidation_prob > 0.7:
                enhanced['primary_findings'].append(
                    f"Pneumonia CONFIRMED (AI confidence: {max(pneumonia_prob, consolidation_prob):.0%})"
                )
                enhanced['clinical_impression'] = "Findings consistent with bacterial pneumonia"
                enhanced['confidence'] = max(pneumonia_prob, consolidation_prob)
                
                # Determine location
                if 'findings' in xray_findings:
                    for finding in xray_findings['findings']:
                        if 'right' in finding.lower():
                            enhanced['primary_findings'].append("Right-sided predominance")
                        elif 'left' in finding.lower():
                            enhanced['primary_findings'].append("Left-sided predominance")
                        elif 'bilateral' in finding.lower():
                            enhanced['primary_findings'].append("Bilateral involvement - consider atypical pneumonia or ARDS")
                
            elif infiltration_prob > 0.5:
                enhanced['primary_findings'].append("Infiltrates present - early pneumonia possible")
                enhanced['clinical_impression'] = "Early pneumonic changes"
                enhanced['follow_up_needed'].append("Repeat CXR in 24-48 hours")
            
            else:
                # Infection suspected but no clear pneumonia
                enhanced['primary_findings'].append("No definite pneumonia on current imaging")
                enhanced['differential_diagnosis'].extend([
                    "Early pneumonia (may not be visible yet)",
                    "Non-pulmonary infection source",
                    "Atypical pneumonia"
                ])
                enhanced['follow_up_needed'].append("Consider CT chest if high clinical suspicion")
        
        # Check for cardiac findings if cardiac issue suspected
        if context['cardiac_issue']:
            cardiomegaly_prob = ai_predictions.get('Cardiomegaly', 0)
            effusion_prob = ai_predictions.get('Effusion', 0)
            edema_prob = ai_predictions.get('Edema', 0)
            
            if cardiomegaly_prob > 0.6:
                enhanced['primary_findings'].append(f"Cardiomegaly present (confidence: {cardiomegaly_prob:.0%})")
            
            if effusion_prob > 0.5:
                enhanced['primary_findings'].append(f"Pleural effusion detected")
                enhanced['follow_up_needed'].append("Consider thoracentesis if large effusion")
            
            if edema_prob > 0.5 or cardiomegaly_prob > 0.6:
                enhanced['clinical_impression'] = "Findings consistent with CHF exacerbation"
                enhanced['differential_diagnosis'].append("Acute decompensated heart failure")
        
        # If no specific context, provide general assessment
        if not enhanced['primary_findings']:
            enhanced['primary_findings'] = xray_findings.get('findings', ['No acute findings'])
            enhanced['clinical_impression'] = xray_findings.get('impression', 'No acute cardiopulmonary process')
        
        return enhanced
    
    async def _correlate_with_labs(self, enhanced_findings: Dict) -> List[str]:
        """
        Correlate imaging findings with lab results
        """
        correlations = []
        
        lab_summary = blackboard.get_latest_finding('lab_analysis_complete')
        if not lab_summary:
            return ["No lab data available for correlation"]
        
        key_labs = lab_summary.get('key_values', {})
        
        # Pneumonia correlation
        if 'pneumonia' in enhanced_findings['clinical_impression'].lower():
            wbc = key_labs.get('wbc', 0)
            crp = key_labs.get('crp', 0)
            
            if wbc > 15 and crp > 50:
                correlations.append(
                    "✅ Imaging findings STRONGLY correlate with lab markers of bacterial infection"
                )
                correlations.append(
                    f"Supporting evidence: WBC {wbc} (elevated), CRP {crp} (markedly elevated)"
                )
            elif wbc < 11 and crp < 20:
                correlations.append(
                    "⚠️ Imaging shows pneumonia but labs suggest viral etiology (normal WBC/CRP)"
                )
                correlations.append(
                    "Consider atypical pneumonia or early bacterial infection"
                )
            else:
                correlations.append(
                    "🔍 Mixed picture - imaging and labs partially correlate"
                )
        
        # Heart failure correlation
        if 'heart failure' in enhanced_findings['clinical_impression'].lower():
            bnp = key_labs.get('bnp', 0)
            
            if bnp > 400:
                correlations.append(
                    f"✅ Elevated BNP ({bnp}) strongly supports heart failure diagnosis"
                )
            else:
                correlations.append(
                    "⚠️ BNP not significantly elevated - consider other causes of imaging findings"
                )
        
        return correlations
    
    async def _communicate_findings(self, enhanced_findings: Dict, correlations: List[str]):
        """
        Share findings with other agents
        """
        # Post primary analysis
        await blackboard.post(
            self.agent_id,
            MessageType.FINDING,
            "xray_analysis_complete",
            {
                'impression': enhanced_findings['clinical_impression'],
                'key_findings': enhanced_findings['primary_findings'],
                'confidence': enhanced_findings['confidence'],
                'correlations': correlations
            },
            Priority.HIGH if enhanced_findings['primary_findings'] else Priority.NORMAL
        )
        
        # If pneumonia confirmed, alert everyone
        if 'pneumonia' in enhanced_findings['clinical_impression'].lower() and enhanced_findings['confidence'] > 0.7:
            await blackboard.post(
                self.agent_id,
                MessageType.ALERT,
                "pneumonia_confirmed_on_imaging",
                {
                    'type': 'Bacterial pneumonia likely' if any('bacterial' in c for c in correlations) else 'Pneumonia',
                    'location': next((f for f in enhanced_findings['primary_findings'] if 'sided' in f or 'bilateral' in f), 'Not specified'),
                    'severity': 'Severe' if 'bilateral' in str(enhanced_findings['primary_findings']) else 'Moderate'
                },
                Priority.HIGH
            )
    
    async def _seek_consensus(self, enhanced_findings: Dict):
        """
        Seek consensus with other agents
        """
        # Post opinion for consensus building
        opinion = f"Based on imaging, primary diagnosis is {enhanced_findings['clinical_impression']}"
        
        blackboard.post_opinion(
            self.agent_id,
            "primary_diagnosis",
            opinion,
            enhanced_findings['confidence']
        )
        
        # Ask specific questions
        if enhanced_findings['differential_diagnosis']:
            await blackboard.ask_question(
                self.agent_id,
                f"Given the imaging shows {enhanced_findings['clinical_impression']}, but differential includes {', '.join(enhanced_findings['differential_diagnosis'][:2])}, what additional tests would help narrow the diagnosis?",
                target_agents=['LabAnalyzer', 'ClinicalDecision']
            )
    
    async def handle_event(self, topic: str, message: Dict):
        """
        Handle events from other agents
        """
        print(f"[{self.name}] Received event: {topic}")
        
        # If severe infection detected, offer to re-review imaging
        if topic == "severe_infection_detected":
            print(f"[{self.name}] 🔍 Severe infection detected by labs - let me look more carefully for subtle pneumonia...")
            
            # Post acknowledgment
            await blackboard.post(
                self.agent_id,
                MessageType.RESPONSE,
                "reviewing_for_infection",
                "Re-examining imaging for subtle signs of pneumonia given lab findings",
                Priority.HIGH
            )
        
        # Respond to questions
        elif topic.startswith("question_"):
            question = message.get('content', '')
            if "additional tests" in question and self.agent_id in str(message.get('target_agents', [])):
                response = "For pneumonia vs atypical pneumonia: Consider CT chest for better characterization. "
                response += "Also recommend blood cultures and respiratory pathogen panel."
                await blackboard.respond_to_question(self.agent_id, topic, response)

# Create the intelligent agent
image_analyzer = IntelligentImageAnalyzerAgent()
