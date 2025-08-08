"""
Healthcare Analytics Agent - Provides unified cost and stay estimates
"""
from typing import Dict
from utils.cost_calculator import calculate_hospital_cost, estimate_length_of_stay
from datetime import datetime, timedelta

class HealthcareAnalyticsAgent:
    """
    Provides consistent healthcare analytics across all views
    """
    
    def __init__(self):
        self.agent_id = "analytics_agent"
        self.name = "Healthcare Analytics"
    
    async def analyze_case(self, analysis_data: Dict) -> Dict:
        """
        Generate unified analytics for a patient case
        """
        # Extract key data
        consensus = analysis_data.get('consensus', {})
        patient_data = analysis_data.get('patient_data') or analysis_data.get('patient', {})
        detailed_findings = analysis_data.get('detailed_findings', {})
        
        # Get diagnosis and risk level
        diagnosis = consensus.get('primary_diagnosis', 'Unknown condition')
        risk_assessment = detailed_findings.get('risk', {})
        risk_level = risk_assessment.get('overall_risk', 'MODERATE')
        age = patient_data.get('age', 65)
        
        # Calculate length of stay
        los_days = estimate_length_of_stay(risk_level, diagnosis)
        
        # Calculate costs
        cost_data = calculate_hospital_cost(risk_level, diagnosis, age, los_days)
        
        # Calculate expected discharge date
        admission_date = datetime.now()
        discharge_date = admission_date + timedelta(days=los_days)
        
        # Generate analytics summary
        analytics = {
            'predicted_length_of_stay': los_days,
            'expected_discharge': discharge_date.strftime('%m/%d/%Y'),
            'estimated_total_cost': cost_data['total_estimated'],
            'cost_breakdown': cost_data['breakdown'],
            'insurance_estimate': cost_data['insurance_estimate'],
            'daily_rate': cost_data['daily_rate'],
            'risk_level': risk_level,
            'primary_diagnosis': diagnosis,
            'stay_type': self._determine_stay_type(risk_level, diagnosis),
            'confidence': self._calculate_confidence(consensus)
        }
        
        # Debug logging
        print(f"\n💰 Healthcare Analytics Calculation:")
        print(f"   Risk Level: {risk_level}")
        print(f"   Diagnosis: {diagnosis}")
        print(f"   Length of Stay: {los_days} days")
        print(f"   Daily Rate: ${cost_data['daily_rate']:,}")
        print(f"   Total Cost: ${cost_data['total_estimated']:,}")
        print(f"   Patient Age: {age}")
        print(f"   Cost Breakdown: {cost_data['breakdown']}")
        print(f"   Insurance Estimate: ${cost_data['insurance_estimate']['with_insurance']:,}")
        print("")
        
        
        return analytics
    
    def _determine_stay_type(self, risk_level: str, diagnosis: str) -> str:
        """
        Determine the type of hospital stay needed
        """
        if risk_level == "CRITICAL" or "sepsis" in diagnosis.lower():
            return "ICU - Intensive monitoring required"
        elif risk_level == "HIGH":
            return "Step-down unit - Close monitoring"
        elif risk_level == "MODERATE":
            return "Standard admission for moderate risk patient"
        else:
            return "Observation - May discharge if stable"
    
    def _calculate_confidence(self, consensus: Dict) -> float:
        """
        Calculate confidence in the analytics
        """
        confidence_level = consensus.get('confidence_level', 'MODERATE')
        
        if 'HIGH' in confidence_level:
            return 0.85
        elif 'MODERATE' in confidence_level:
            return 0.70
        else:
            return 0.50

# Create singleton instance
healthcare_analytics = HealthcareAnalyticsAgent()
