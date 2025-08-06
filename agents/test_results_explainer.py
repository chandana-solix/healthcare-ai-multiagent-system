"""
AI-Powered Test Results Explainer Agent
Translates all agent findings into patient-friendly language using actual AI
"""
from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime

# Import AI utilities
try:
    from utils.medical_intelligence import MedicalIntelligence
    ai_available = True
except ImportError:
    ai_available = False
    print("⚠️  Medical Intelligence not available - using template mode")

class TestResultsExplainerAgent:
    """
    AI agent that explains medical test results in patient-friendly language
    Based on ALL agent findings but translated for patient understanding
    """
    
    def __init__(self):
        self.agent_id = "TestExplainer"
        self.name = "Patient Educator"
        self.ai = MedicalIntelligence() if ai_available else None
    
    async def explain_test_results(self, analysis_data: Dict) -> Dict:
        """
        Generate personalized explanation of test results based on all agent findings
        """
        # Extract all agent findings
        patient = analysis_data.get('patient', {})
        lab_findings = analysis_data.get('detailed_findings', {}).get('lab', {})
        imaging_findings = analysis_data.get('detailed_findings', {}).get('imaging', {})
        risk_data = analysis_data.get('detailed_findings', {}).get('risk', {})
        clinical_data = analysis_data.get('detailed_findings', {}).get('clinical_decision', {})
        consensus = analysis_data.get('consensus', {})
        agent_communications = analysis_data.get('agent_communication', {})
        
        # Generate comprehensive explanation
        explanation = {
            'greeting': self._generate_greeting(patient),
            'summary': await self._create_executive_summary(patient, consensus, risk_data),
            'lab_explanation': await self._explain_lab_results(lab_findings, patient),
            'imaging_explanation': await self._explain_imaging(imaging_findings, patient),
            'risk_explanation': await self._explain_risk_assessment(risk_data, lab_findings),
            'diagnosis_explanation': await self._explain_diagnosis(
                consensus.get('primary_diagnosis', ''),
                clinical_data.get('confidence', 0),
                consensus.get('confidence_level', ''),
                agent_communications
            ),
            'treatment_rationale': await self._explain_why_this_treatment(
                clinical_data,
                risk_data.get('overall_risk', ''),
                consensus.get('disposition', '')
            ),
            'what_to_expect': await self._explain_timeline(
                consensus.get('primary_diagnosis', ''),
                risk_data.get('overall_risk', ''),
                patient.get('age', 0)
            ),
            'consensus_note': await self._explain_medical_agreement(
                consensus.get('confidence_level', ''),
                agent_communications
            ),
            'reassurance': await self._provide_contextual_reassurance(
                consensus.get('primary_diagnosis', ''),
                risk_data.get('overall_risk', ''),
                patient
            ),
            'personalized_narrative': await self._generate_complete_narrative(
                analysis_data
            )
        }
        
        return explanation
    
    def _generate_greeting(self, patient: Dict) -> str:
        """Generate personalized greeting"""
        name = patient.get('name', 'there')
        return f"Hello {name}! Here's what your medical tests tell us about your health:"
    
    async def _create_executive_summary(self, patient: Dict, consensus: Dict, risk_data: Dict) -> str:
        """Create a one-paragraph summary of everything"""
        diagnosis = consensus.get('primary_diagnosis', 'your condition')
        risk = risk_data.get('overall_risk', 'MODERATE')
        symptom = patient.get('chief_complaint', 'your symptoms')
        
        if self.ai and ai_available:
            prompt = f"""
            Create a compassionate one-paragraph executive summary for a patient explaining their test results.
            
            Patient complaint: {symptom}
            Diagnosis: {diagnosis}
            Risk level: {risk}
            
            Rules:
            - Be clear but not alarming
            - Use simple language
            - Acknowledge their symptoms
            - Explain what was found
            - Indicate urgency appropriately
            - Keep it to 2-3 sentences
            """
            
            summary = await self.ai.generate_patient_explanation(prompt)
            return summary
        else:
            # Fallback template
            summary = f"Based on all your test results and {symptom}, our medical team has determined "
            
            if risk == 'HIGH' or risk == 'CRITICAL':
                summary += f"you have {diagnosis} that requires prompt hospital treatment. "
                summary += "While this needs immediate attention, it's a condition we treat successfully every day."
            else:
                summary += f"you likely have {diagnosis}. "
                summary += "The good news is this is very treatable with the right care."
            
            return summary
    
    async def _explain_lab_results(self, lab_findings: Dict, patient: Dict) -> str:
        """Explain lab results in patient-friendly terms"""
        patterns = lab_findings.get('patterns', [])
        key_values = lab_findings.get('key_values', {})
        age = patient.get('age', 50)
        
        if self.ai and ai_available:
            prompt = f"""
            Explain these lab results to a {age}-year-old patient in simple, non-scary language:
            
            Key findings:
            - Patterns: {patterns}
            - WBC: {key_values.get('wbc', 'normal')}
            - CRP: {key_values.get('crp', 'normal')}
            - Other values: {json.dumps(key_values, indent=2)}
            
            Use analogies they can understand. Be accurate but reassuring.
            Explain what the abnormal values mean in practical terms.
            """
            
            return await self.ai.generate_patient_explanation(prompt)
        
        # Fallback template logic
        explanation = ""
        
        # Check for infection patterns
        if 'SEVERE_BACTERIAL_INFECTION' in patterns or 'BACTERIAL_INFECTION' in patterns:
            wbc = key_values.get('wbc', 0)
            crp = key_values.get('crp', 0)
            
            if age > 65:
                explanation = f"Your blood tests show your body is fighting hard against an infection. "
                explanation += f"Your white blood cells (infection fighters) are at {wbc} - think of this "
                explanation += f"like having many more security guards than usual (normal is 4-11). "
            else:
                explanation = f"Your blood work reveals a significant infection. Your white blood cells "
                explanation += f"are at {wbc} compared to the normal 4-11 - imagine your immune system "
                explanation += f"calling in all available reinforcements to fight off invaders. "
            
            if crp > 100:
                explanation += f"Your inflammation level (CRP) is also quite high at {crp}, "
                explanation += "which confirms your body is in active battle mode against this infection."
        
        elif patterns:
            explanation = "Your blood tests show some abnormalities that help us understand what's happening in your body."
        
        else:
            explanation = "Your blood tests are largely within normal ranges, which is reassuring."
        
        return explanation
    
    async def _explain_imaging(self, imaging_findings: Dict, patient: Dict) -> str:
        """Explain imaging findings simply"""
        impression = imaging_findings.get('impression', '')
        findings = imaging_findings.get('key_findings', [])
        
        if self.ai and ai_available:
            prompt = f"""
            Explain these X-ray findings to a patient in simple terms:
            
            Impression: {impression}
            Findings: {findings}
            
            Use visual analogies (like clouds, shadows, etc).
            Be accurate but not frightening.
            Help them understand what the doctors see.
            """
            
            return await self.ai.generate_patient_explanation(prompt)
        
        # Fallback template
        if 'pneumonia' in impression.lower():
            explanation = "Your chest X-ray shows signs consistent with pneumonia. "
            
            # Count significant findings
            significant = [f for f in findings if any(x in f.lower() for x in ['consolidation', 'infiltrat'])]
            
            if significant:
                explanation += "We can see areas in your lungs that appear cloudy or dense - "
                explanation += "think of your lungs like sponges that should be full of air, "
                explanation += "but some areas have fluid or infection instead."
            
        elif 'normal' in impression.lower():
            explanation = "Good news - your chest X-ray looks normal, with no signs of pneumonia or other lung problems."
        
        else:
            explanation = "Your chest X-ray shows some changes that need to be considered along with your other symptoms."
        
        return explanation
    
    async def _explain_risk_assessment(self, risk_data: Dict, lab_findings: Dict) -> str:
        """Explain why risk might be high despite normal vital signs"""
        overall_risk = risk_data.get('overall_risk', 'MODERATE')
        mews = risk_data.get('key_scores', {}).get('MEWS', {})
        risk_factors = risk_data.get('risk_factors', [])
        
        if self.ai and ai_available:
            prompt = f"""
            Explain to a patient why their risk assessment is {overall_risk} when their vital signs might seem okay.
            
            MEWS score: {mews.get('score', 0)}
            Risk factors: {risk_factors}
            Lab patterns: {lab_findings.get('patterns', [])}
            
            Help them understand why we're concerned without causing panic.
            Explain the benefit of catching things early.
            """
            
            return await self.ai.generate_patient_explanation(prompt)
        
        # Fallback template
        if overall_risk in ['HIGH', 'CRITICAL'] and mews.get('score', 0) == 0:
            explanation = "You might wonder why we're concerned when some of your basic measurements "
            explanation += "(like blood pressure and heart rate) seem okay. The answer is in your blood tests - "
            explanation += "they show infection levels that need immediate treatment, even though your vital signs "
            explanation += "are currently stable. This actually helps us catch and treat the infection before it affects "
            explanation += "your vital signs."
        else:
            explanation = f"Your overall risk assessment shows you need "
            if overall_risk == 'CRITICAL':
                explanation += "immediate intensive care to ensure the best outcome."
            elif overall_risk == 'HIGH':
                explanation += "close monitoring and prompt treatment in the hospital."
            else:
                explanation += "medical attention to prevent this from becoming more serious."
        
        return explanation
    
    async def _explain_diagnosis(self, diagnosis: str, confidence: float, 
                               consensus_level: str, agent_communications: Dict) -> str:
        """Explain the diagnosis in simple terms"""
        
        if self.ai and ai_available:
            # Extract key debates from agent communications
            debates = agent_communications.get('conversation_highlights', [])
            
            prompt = f"""
            Explain this diagnosis to a patient:
            
            Diagnosis: {diagnosis}
            Doctor confidence: {confidence:.0%}
            Team agreement level: {consensus_level}
            
            {f"Note: The medical team had some discussion: {debates}" if 'LOW' in consensus_level else ""}
            
            Explain what the condition is in simple terms.
            If there was debate, reassure that discussion is good.
            Focus on treatment effectiveness.
            """
            
            return await self.ai.generate_patient_explanation(prompt)
        
        # Fallback template
        explanation = ""
        
        if 'pneumonia' in diagnosis.lower():
            if 'bacterial' in diagnosis.lower():
                explanation = "You have bacterial pneumonia - this means bacteria have caused an infection in your lungs. "
                explanation += "This is different from a common cold or flu because it affects the air sacs in your lungs, "
                explanation += "making it harder to breathe. The good news is that bacterial pneumonia responds very well "
                explanation += "to antibiotics."
            else:
                explanation = f"You have {diagnosis}, which is an infection in your lungs that makes breathing difficult."
        
        elif 'sepsis' in diagnosis.lower():
            explanation = "You have a serious infection that has spread through your bloodstream. "
            explanation += "This requires immediate treatment, but with proper care, most people recover fully."
        
        else:
            explanation = f"Based on all tests, you have {diagnosis}."
        
        # Add confidence note if low consensus
        if 'LOW' in consensus_level:
            explanation += " Your medical team carefully reviewed and discussed your case to ensure "
            explanation += "the most accurate diagnosis."
        
        return explanation
    
    async def _explain_why_this_treatment(self, clinical_data: Dict, risk_level: str, disposition: str) -> str:
        """Explain treatment rationale"""
        medications = clinical_data.get('key_medications', [])
        
        if self.ai and ai_available:
            prompt = f"""
            Explain why this treatment plan was chosen:
            
            Risk level: {risk_level}
            Disposition: {disposition}
            Medications: {medications}
            
            Help the patient understand:
            - Why hospital/ICU admission if needed
            - How the medications work
            - Why IV is better than pills (if applicable)
            - What monitoring means
            
            Be reassuring about the care they'll receive.
            """
            
            return await self.ai.generate_patient_explanation(prompt)
        
        # Fallback template
        explanation = "Your treatment plan includes:\n\n"
        
        if 'ICU' in disposition:
            explanation += "• Intensive Care Unit admission - You need the highest level of monitoring "
            explanation += "to ensure you respond well to treatment.\n"
        elif 'admit' in disposition.lower():
            explanation += "• Hospital admission - You need IV medications and professional monitoring "
            explanation += "that can only be provided in the hospital.\n"
        
        if medications:
            explanation += f"• Antibiotics ({medications[0].split()[0]}) - These will fight the bacterial infection. "
            explanation += "IV antibiotics work faster and stronger than pills.\n"
        
        explanation += "• Oxygen support if needed - To ensure your body gets enough oxygen while healing.\n"
        explanation += "• Regular monitoring - Nurses will check on you frequently to track your improvement."
        
        return explanation
    
    async def _explain_timeline(self, diagnosis: str, risk_level: str, age: int) -> str:
        """Explain expected timeline"""
        
        if self.ai and ai_available:
            prompt = f"""
            Explain the recovery timeline for:
            
            Diagnosis: {diagnosis}
            Risk level: {risk_level}
            Patient age: {age}
            
            Include:
            - When they'll start feeling better
            - Day-by-day improvements
            - Total recovery time
            - Age considerations if relevant
            
            Be realistic but encouraging.
            """
            
            return await self.ai.generate_patient_explanation(prompt)
        
        # Fallback template
        if 'pneumonia' in diagnosis.lower():
            timeline = "Most people with pneumonia start feeling better within 2-3 days of starting antibiotics. "
            timeline += "You'll likely notice:\n"
            timeline += "• Day 1-2: Fever should start to break\n"
            timeline += "• Day 2-3: Breathing becomes easier\n"
            timeline += "• Day 3-5: Energy starts returning\n"
            
            if age > 65:
                timeline += f"\nAt age {age}, recovery might take a bit longer, which is completely normal."
        else:
            timeline = "Recovery time varies, but most people see improvement within a few days of treatment."
        
        return timeline
    
    async def _explain_medical_agreement(self, consensus_level: str, agent_communication: Dict) -> str:
        """Explain how medical team reached decision"""
        
        if self.ai and ai_available:
            debates = agent_communication.get('total_messages', 0)
            questions = agent_communication.get('questions_asked', 0)
            
            prompt = f"""
            Explain how the medical team reached their decision:
            
            Agreement level: {consensus_level}
            Total discussions: {debates}
            Questions raised: {questions}
            
            If LOW consensus: reassure that debate is good
            If HIGH consensus: indicate quick agreement
            
            Keep it brief and reassuring.
            """
            
            return await self.ai.generate_patient_explanation(prompt)
        
        # Fallback template
        if 'HIGH' in consensus_level:
            return "Your medical team quickly agreed on your diagnosis and treatment plan."
        elif 'LOW' in consensus_level:
            explanation = "Your case was thoroughly reviewed by our medical team. While there was initial "
            explanation += "discussion about the exact diagnosis, all doctors agreed you need hospital treatment. "
            explanation += "This kind of medical discussion is actually good - it means your case received extra attention."
            return explanation
        else:
            return "Your medical team reviewed all your tests and agreed on the best treatment approach."
    
    async def _provide_contextual_reassurance(self, diagnosis: str, risk_level: str, patient: Dict) -> str:
        """Provide appropriate reassurance"""
        age = patient.get('age', 50)
        
        if self.ai and ai_available:
            prompt = f"""
            Provide reassurance to a {age}-year-old patient with:
            
            Diagnosis: {diagnosis}
            Risk level: {risk_level}
            
            Be:
            - Honest about seriousness if HIGH/CRITICAL
            - Reassuring about treatment success
            - Specific about positive outcomes
            - Age-appropriate in tone
            
            2-3 sentences maximum.
            """
            
            return await self.ai.generate_patient_explanation(prompt)
        
        # Fallback template
        if risk_level in ['HIGH', 'CRITICAL']:
            reassurance = "While your condition is serious and needs immediate treatment, "
            reassurance += "it's important to know that we treat patients with similar conditions every day. "
            reassurance += "With proper treatment, most people make a full recovery. "
            reassurance += "You're in good hands, and we'll monitor you closely."
        else:
            reassurance = f"This is a treatable condition. With proper care, most people with {diagnosis} "
            reassurance += "recover completely and return to their normal activities."
        
        return reassurance
    
    async def _generate_complete_narrative(self, analysis_data: Dict) -> str:
        """
        Generate a complete, cohesive narrative that tells the patient's story
        """
        if self.ai and ai_available:
            # Compile all the key information
            patient = analysis_data.get('patient', {})
            consensus = analysis_data.get('consensus', {})
            lab_findings = analysis_data.get('detailed_findings', {}).get('lab', {})
            imaging_findings = analysis_data.get('detailed_findings', {}).get('imaging', {})
            risk_data = analysis_data.get('detailed_findings', {}).get('risk', {})
            
            prompt = f"""
            Create a cohesive, personal narrative explaining the patient's test results.
            Write it as if you're sitting with them, explaining everything in a caring way.
            
            Patient: {patient.get('age')}y {patient.get('gender')} with {patient.get('chief_complaint')}
            Diagnosis: {consensus.get('primary_diagnosis')}
            Risk: {risk_data.get('overall_risk')}
            
            Lab highlights: {lab_findings.get('patterns', [])}
            Imaging: {imaging_findings.get('impression', '')}
            Treatment plan: {consensus.get('disposition')}
            
            Structure:
            1. Acknowledge their symptoms and concerns
            2. Explain what the tests found (labs and X-ray)
            3. Connect findings to their diagnosis
            4. Explain why the treatment is needed
            5. Provide timeline and reassurance
            
            Make it personal, warm, and educational without being condescending.
            Use "you" and "your" throughout. About 2-3 paragraphs.
            """
            
            return await self.ai.generate_patient_explanation(prompt)
        
        # Fallback comprehensive narrative
        patient = analysis_data.get('patient', {})
        diagnosis = analysis_data.get('consensus', {}).get('primary_diagnosis', '')
        risk = analysis_data.get('detailed_findings', {}).get('risk', {}).get('overall_risk', '')
        
        narrative = f"I understand you came in with {patient.get('chief_complaint', 'concerning symptoms')}, "
        narrative += "and I know you must be worried. Let me walk you through what we found and what it means for you.\n\n"
        
        narrative += "Your blood tests and chest X-ray have given us a clear picture of what's happening. "
        narrative += f"The tests show that you have {diagnosis}, which explains why you've been feeling this way. "
        narrative += "While this is certainly something that needs treatment, I want you to know that this is "
        narrative += "a condition we see regularly and treat very successfully.\n\n"
        
        if risk in ['HIGH', 'CRITICAL']:
            narrative += "Because of the extent of the infection shown in your tests, we need to start treatment "
            narrative += "in the hospital right away. This isn't meant to alarm you - it's actually good that we "
            narrative += "caught this now. With IV antibiotics and proper monitoring, most patients start feeling "
            narrative += "noticeably better within 24-48 hours. Our team will be watching you closely to ensure "
            narrative += "you're responding well to treatment."
        else:
            narrative += "The good news is that we've caught this at a point where treatment can be very effective. "
            narrative += "With the right antibiotics and care, you should start feeling better soon."
        
        return narrative

# Create explainer instance
test_explainer = TestResultsExplainerAgent()

# Standalone function for easy integration
async def generate_patient_explanation(analysis_data: Dict) -> Dict:
    """
    Generate complete patient-friendly explanation of test results
    """
    return await test_explainer.explain_test_results(analysis_data)
