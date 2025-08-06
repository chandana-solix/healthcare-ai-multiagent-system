"""
Medical Intelligence: Real Clinical Scoring Systems and Guidelines
"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class ClinicalScore:
    name: str
    score: int
    max_score: int
    criteria_met: List[str]
    interpretation: str
    risk_level: RiskLevel
    recommendations: List[str]

class MedicalIntelligence:
    """
    Real medical scoring systems and clinical decision support
    """
    
    def __init__(self):
        """Initialize medical intelligence with AI capability if available"""
        self.ai_available = False
        self.ai_client = None
        self._check_ai_availability()
    
    def _check_ai_availability(self):
        """Check if AI models are available"""
        try:
            import requests
            # Check if Ollama is running
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            if response.status_code == 200:
                self.ai_available = True
                print("✅ AI models available via Ollama")
            else:
                print("⚠️  Ollama not responding - using template mode")
        except:
            print("⚠️  No AI service found - using template mode")
    
    async def generate_patient_explanation(self, prompt: str) -> str:
        """
        Generate patient-friendly explanation using AI or templates
        """
        if self.ai_available:
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        'http://localhost:11434/api/generate',
                        json={
                            'model': 'llama3.2:latest',
                            'prompt': prompt,
                            'stream': False,
                            'temperature': 0.7,
                            'max_tokens': 500
                        }
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data.get('response', self._fallback_explanation(prompt))
            except Exception as e:
                print(f"AI generation error: {e}")
        
        # Fallback to template-based response
        return self._fallback_explanation(prompt)
    
    def _fallback_explanation(self, prompt: str) -> str:
        """
        Generate template-based explanation when AI is not available
        """
        # Extract key information from prompt
        prompt_lower = prompt.lower()
        
        if "executive summary" in prompt_lower:
            if "high" in prompt_lower or "critical" in prompt_lower:
                return "Your test results show a condition that requires immediate medical attention. While this needs prompt treatment, our medical team is experienced in managing these cases and will provide you with the best care possible."
            else:
                return "Your test results indicate a treatable condition. With proper care and medication, most patients with similar conditions recover well."
        
        elif "lab results" in prompt_lower:
            if "infection" in prompt_lower or "bacterial" in prompt_lower:
                return "Your blood tests show signs of infection. Your body's defense system is working hard to fight it off, which is why some of your blood values are elevated. The good news is that infections like this typically respond well to antibiotics."
            else:
                return "Your blood tests provide important information about how your body is functioning. Some values may be outside the normal range, which helps us understand what's happening and how best to treat you."
        
        elif "x-ray" in prompt_lower or "imaging" in prompt_lower:
            if "pneumonia" in prompt_lower:
                return "Your chest X-ray shows changes in your lungs consistent with pneumonia. Think of it like areas where your lung tissue has become inflamed or filled with fluid instead of air. This explains your breathing difficulties."
            else:
                return "Your imaging results help us see what's happening inside your body. The findings guide our treatment decisions."
        
        elif "treatment" in prompt_lower:
            if "hospital" in prompt_lower or "admission" in prompt_lower:
                return "You'll need to be admitted to the hospital for treatment. This allows us to give you IV medications that work faster than pills, monitor your progress closely, and adjust treatment as needed. Our nursing staff will check on you regularly."
            else:
                return "Your treatment plan is designed to address your specific condition effectively. We'll monitor your progress and adjust as needed."
        
        elif "timeline" in prompt_lower or "recovery" in prompt_lower:
            return "Most patients start feeling better within 2-3 days of starting treatment. You'll likely notice your fever breaking first, followed by easier breathing and returning energy. Full recovery typically takes 1-2 weeks."
        
        else:
            # Generic helpful response
            return "Based on your test results and symptoms, we have a clear understanding of your condition and the best way to treat it. Our medical team will ensure you receive appropriate care."
    
    @staticmethod
    def calculate_sirs(vitals: Dict, labs: Dict) -> ClinicalScore:
        """
        SIRS (Systemic Inflammatory Response Syndrome) criteria
        Used to screen for sepsis
        """
        score = 0
        criteria = []
        
        # Temperature: <36°C or >38°C
        temp_c = vitals.get('temperature_c', 37)
        if temp_c < 36 or temp_c > 38:
            score += 1
            criteria.append(f"Temperature: {temp_c}°C")
        
        # Heart rate > 90
        hr = vitals.get('heart_rate', 70)
        if hr > 90:
            score += 1
            criteria.append(f"Tachycardia: HR {hr}")
        
        # Respiratory rate > 20 or PaCO2 < 32
        rr = vitals.get('respiratory_rate', 16)
        if rr > 20:
            score += 1
            criteria.append(f"Tachypnea: RR {rr}")
        
        # WBC < 4 or > 12 or > 10% bands
        wbc = labs.get('wbc')
        if wbc and (wbc < 4 or wbc > 12):
            score += 1
            criteria.append(f"Abnormal WBC: {wbc}")
        
        # Interpretation
        if score >= 2:
            interpretation = "Meets SIRS criteria - evaluate for infection source"
            risk_level = RiskLevel.HIGH if score >= 3 else RiskLevel.MODERATE
            recommendations = [
                "Blood cultures x2",
                "Lactate level",
                "Broad spectrum antibiotics within 1 hour",
                "IV fluid resuscitation"
            ]
        else:
            interpretation = "Does not meet SIRS criteria"
            risk_level = RiskLevel.LOW
            recommendations = ["Monitor vital signs", "Recheck if clinical change"]
        
        return ClinicalScore(
            name="SIRS",
            score=score,
            max_score=4,
            criteria_met=criteria,
            interpretation=interpretation,
            risk_level=risk_level,
            recommendations=recommendations
        )
    
    @staticmethod
    def calculate_curb65(patient_data: Dict, vitals: Dict, labs: Dict) -> ClinicalScore:
        """
        CURB-65 Score for pneumonia severity
        """
        score = 0
        criteria = []
        
        # Confusion (would need mental status assessment)
        # For now, check if mentioned in chief complaint
        if 'confusion' in patient_data.get('chief_complaint', '').lower():
            score += 1
            criteria.append("Confusion present")
        
        # Urea > 7 mmol/L (BUN > 19 mg/dL)
        bun = labs.get('bun')
        if bun and bun > 19:
            score += 1
            criteria.append(f"Elevated BUN: {bun} mg/dL")
        
        # Respiratory rate >= 30
        rr = vitals.get('respiratory_rate', 16)
        if rr >= 30:
            score += 1
            criteria.append(f"High respiratory rate: {rr}")
        
        # Blood pressure: SBP < 90 or DBP <= 60
        bp_sys = vitals.get('blood_pressure_systolic', 120)
        bp_dia = vitals.get('blood_pressure_diastolic', 80)
        if bp_sys < 90 or bp_dia <= 60:
            score += 1
            criteria.append(f"Hypotension: {bp_sys}/{bp_dia}")
        
        # Age >= 65
        age = patient_data.get('age', 0)
        if age >= 65:
            score += 1
            criteria.append(f"Age ≥65: {age} years")
        
        # Interpretation
        if score <= 1:
            interpretation = "Low risk - consider outpatient treatment"
            risk_level = RiskLevel.LOW
            recommendations = ["Oral antibiotics", "Close follow-up in 24-48h"]
        elif score == 2:
            interpretation = "Moderate risk - consider admission"
            risk_level = RiskLevel.MODERATE
            recommendations = ["Hospital admission", "IV antibiotics", "Monitor O2"]
        else:
            interpretation = "High risk - admit, consider ICU"
            risk_level = RiskLevel.HIGH if score == 3 else RiskLevel.CRITICAL
            recommendations = ["ICU evaluation", "Aggressive treatment", "Consider vasopressors"]
        
        return ClinicalScore(
            name="CURB-65",
            score=score,
            max_score=5,
            criteria_met=criteria,
            interpretation=interpretation,
            risk_level=risk_level,
            recommendations=recommendations
        )
    
    @staticmethod
    def calculate_mews(vitals: Dict) -> ClinicalScore:
        """
        Modified Early Warning Score (MEWS)
        Predicts clinical deterioration
        """
        score = 0
        criteria = []
        
        # Respiratory rate
        rr = vitals.get('respiratory_rate', 16)
        if rr < 9:
            score += 2
            criteria.append(f"Very low RR: {rr}")
        elif rr >= 9 and rr <= 14:
            score += 0
        elif rr >= 15 and rr <= 20:
            score += 1
            criteria.append(f"Mildly elevated RR: {rr}")
        elif rr >= 21 and rr <= 29:
            score += 2
            criteria.append(f"Elevated RR: {rr}")
        else:  # >= 30
            score += 3
            criteria.append(f"Very high RR: {rr}")
        
        # Heart rate
        hr = vitals.get('heart_rate', 80)
        if hr < 40:
            score += 2
            criteria.append(f"Bradycardia: {hr}")
        elif hr >= 40 and hr <= 50:
            score += 1
            criteria.append(f"Low HR: {hr}")
        elif hr >= 51 and hr <= 100:
            score += 0
        elif hr >= 101 and hr <= 110:
            score += 1
            criteria.append(f"Mild tachycardia: {hr}")
        elif hr >= 111 and hr <= 129:
            score += 2
            criteria.append(f"Tachycardia: {hr}")
        else:  # >= 130
            score += 3
            criteria.append(f"Severe tachycardia: {hr}")
        
        # Systolic BP
        sbp = vitals.get('blood_pressure_systolic', 120)
        if sbp < 70:
            score += 3
            criteria.append(f"Severe hypotension: {sbp}")
        elif sbp >= 70 and sbp <= 80:
            score += 2
            criteria.append(f"Hypotension: {sbp}")
        elif sbp >= 81 and sbp <= 100:
            score += 1
            criteria.append(f"Low BP: {sbp}")
        elif sbp >= 101 and sbp <= 199:
            score += 0
        else:  # >= 200
            score += 2
            criteria.append(f"Severe hypertension: {sbp}")
        
        # Temperature
        temp_c = vitals.get('temperature_c', 37)
        if temp_c < 35:
            score += 2
            criteria.append(f"Hypothermia: {temp_c}°C")
        elif temp_c >= 35 and temp_c <= 38.4:
            score += 0
        else:  # > 38.4
            score += 2
            criteria.append(f"Fever: {temp_c}°C")
        
        # Level of consciousness (assume alert for now)
        score += 0  # Would need actual assessment
        
        # Interpretation
        if score >= 5:
            interpretation = "High risk of deterioration"
            risk_level = RiskLevel.CRITICAL
            recommendations = ["Urgent medical review", "Consider ICU", "Increase monitoring frequency"]
        elif score >= 3:
            interpretation = "Moderate risk - close monitoring needed"
            risk_level = RiskLevel.MODERATE
            recommendations = ["Increase observation frequency", "Senior review", "Consider escalation"]
        else:
            interpretation = "Low risk - routine monitoring"
            risk_level = RiskLevel.LOW
            recommendations = ["Continue routine observations", "Monitor trend"]
        
        return ClinicalScore(
            name="MEWS",
            score=score,
            max_score=14,
            criteria_met=criteria,
            interpretation=interpretation,
            risk_level=risk_level,
            recommendations=recommendations
        )
    
    @staticmethod
    def calculate_qsofa(vitals: Dict) -> ClinicalScore:
        """
        Quick SOFA (qSOFA) for sepsis screening outside ICU
        """
        score = 0
        criteria = []
        
        # Respiratory rate >= 22
        rr = vitals.get('respiratory_rate', 16)
        if rr >= 22:
            score += 1
            criteria.append(f"High respiratory rate: {rr}")
        
        # Altered mental status (would need GCS)
        # For now, skip this criterion
        
        # Systolic BP <= 100
        sbp = vitals.get('blood_pressure_systolic', 120)
        if sbp <= 100:
            score += 1
            criteria.append(f"Low systolic BP: {sbp}")
        
        # Interpretation
        if score >= 2:
            interpretation = "High risk for poor outcome - suspect sepsis"
            risk_level = RiskLevel.HIGH
            recommendations = [
                "Initiate sepsis protocol",
                "Obtain lactate",
                "Blood cultures",
                "Start antibiotics within 1 hour"
            ]
        else:
            interpretation = "Low risk by qSOFA"
            risk_level = RiskLevel.LOW
            recommendations = ["Monitor closely", "Reassess if deterioration"]
        
        return ClinicalScore(
            name="qSOFA",
            score=score,
            max_score=3,
            criteria_met=criteria,
            interpretation=interpretation,
            risk_level=risk_level,
            recommendations=recommendations
        )
    
    @staticmethod
    def assess_sepsis_risk(sirs: ClinicalScore, qsofa: ClinicalScore, labs: Dict) -> Dict:
        """
        Comprehensive sepsis risk assessment
        """
        risk_factors = []
        
        # Check SIRS
        if sirs.score >= 2:
            risk_factors.append("Meets SIRS criteria")
        
        # Check qSOFA
        if qsofa.score >= 2:
            risk_factors.append("Positive qSOFA")
        
        # Check lactate
        lactate = labs.get('lactate', 1.0)
        if lactate and lactate > 2:
            risk_factors.append(f"Elevated lactate: {lactate}")
        
        # Check organ dysfunction markers
        creatinine = labs.get('creatinine', 1.0)
        if creatinine and creatinine > 1.5:
            risk_factors.append(f"Kidney dysfunction: Cr {creatinine}")
        
        # Overall assessment
        if len(risk_factors) >= 3 or (lactate and lactate > 4):
            return {
                'risk': 'SEVERE SEPSIS/SEPTIC SHOCK',
                'action': 'IMMEDIATE sepsis bundle activation',
                'factors': risk_factors
            }
        elif len(risk_factors) >= 2:
            return {
                'risk': 'SEPSIS LIKELY',
                'action': 'Start sepsis protocol',
                'factors': risk_factors
            }
        else:
            return {
                'risk': 'LOW SEPSIS RISK',
                'action': 'Monitor and reassess',
                'factors': risk_factors
            }
    
    @staticmethod
    def get_antibiotic_recommendations(diagnosis: str, allergies: List[str], 
                                      kidney_function: Optional[float] = None) -> Dict:
        """
        Evidence-based antibiotic recommendations
        """
        recommendations = {
            'pneumonia': {
                'first_line': ['Ceftriaxone 1g IV daily', 'Azithromycin 500mg IV daily'],
                'penicillin_allergy': ['Levofloxacin 750mg IV daily'],
                'severe': ['Ceftriaxone 2g IV daily', 'Azithromycin 500mg IV daily', 
                          'Consider adding Vancomycin']
            },
            'sepsis_unknown_source': {
                'first_line': ['Piperacillin-tazobactam 4.5g IV q6h', 'Vancomycin 15mg/kg IV q12h'],
                'penicillin_allergy': ['Ciprofloxacin 400mg IV q12h', 'Vancomycin 15mg/kg IV q12h'],
                'severe': ['Meropenem 1g IV q8h', 'Vancomycin 15mg/kg IV q12h']
            },
            'uti': {
                'first_line': ['Ceftriaxone 1g IV daily'],
                'penicillin_allergy': ['Ciprofloxacin 400mg IV q12h'],
                'severe': ['Piperacillin-tazobactam 4.5g IV q8h']
            }
        }
        
        # Get base recommendation
        abx_options = recommendations.get(diagnosis.lower(), recommendations['sepsis_unknown_source'])
        
        # Check for allergies
        has_penicillin_allergy = any('penicillin' in allergy.lower() for allergy in allergies)
        
        if has_penicillin_allergy:
            selected = abx_options.get('penicillin_allergy', abx_options['first_line'])
        else:
            selected = abx_options['first_line']
        
        # Adjust for kidney function if needed
        if kidney_function and kidney_function < 50:
            selected = [abx + " (adjust dose for GFR)" for abx in selected]
        
        return {
            'antibiotics': selected,
            'notes': 'Obtain cultures before starting antibiotics',
            'duration': '7-10 days typical, adjust based on response'
        }

# Additional pattern recognition
class ClinicalPatterns:
    """
    Recognize clinical patterns from lab and vital combinations
    """
    
    @staticmethod
    def identify_infection_pattern(labs: Dict, vitals: Dict) -> Optional[str]:
        """
        Identify infection patterns from labs and vitals
        """
        wbc = labs.get('wbc')
        crp = labs.get('crp')
        temp_c = vitals.get('temperature_c', 37)
        
        # Bacterial infection pattern
        if (wbc and crp and wbc > 15 and crp > 50) or (crp and crp > 100):
            if temp_c > 38.5:
                return "SEVERE_BACTERIAL_INFECTION"
            else:
                return "BACTERIAL_INFECTION"
        
        # Check CRP alone if WBC missing
        if crp and crp > 50:
            return "INFLAMMATORY_PROCESS"
        
        # Viral pattern
        if wbc and crp and (wbc < 4 or (wbc > 4 and wbc < 11 and crp < 20)):
            if temp_c > 37.5:
                return "VIRAL_INFECTION"
        
        # If normal WBC but missing, check other indicators
        if not wbc and crp and crp < 10 and temp_c < 37.5:
            return None
        
        # Sepsis pattern
        lactate = labs.get('lactate')
        if wbc and ((wbc > 12 or wbc < 4) and temp_c > 38 and lactate and lactate > 2):
            return "SEPSIS_PATTERN"
        
        return None
    
    @staticmethod
    def identify_cardiac_pattern(labs: Dict, vitals: Dict) -> Optional[str]:
        """
        Identify cardiac patterns
        """
        bnp = labs.get('bnp')
        troponin = labs.get('troponin')
        
        # Heart failure pattern
        if bnp and bnp > 400:
            if bnp > 900:
                return "ACUTE_HEART_FAILURE"
            else:
                return "HEART_FAILURE_EXACERBATION"
        
        # MI pattern
        if troponin and troponin > 0.04:
            return "MYOCARDIAL_INJURY"
        
        return None
