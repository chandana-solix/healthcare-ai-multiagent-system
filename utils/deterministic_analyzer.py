"""
Deterministic Medical Analysis - Provides consistent results for the same inputs
"""
import hashlib
import json
from typing import Dict, List, Any

class DeterministicAnalyzer:
    """Provides consistent medical analysis based on clear rules"""
    
    @staticmethod
    def analyze_patient(patient_data: Dict, lab_values: Dict, xray_findings: List[str]) -> Dict:
        """
        Deterministic analysis based on medical rules
        Returns the SAME result for the SAME input every time
        """
        
        # Create a hash of inputs to ensure consistency
        input_hash = hashlib.md5(
            json.dumps({
                'age': patient_data.get('age'),
                'vitals': patient_data.get('vitals'),
                'labs': lab_values,
                'xray': sorted(xray_findings)
            }, sort_keys=True).encode()
        ).hexdigest()
        
        # Extract key values
        age = patient_data.get('age', 0)
        vitals = patient_data.get('vitals', {})
        temp = vitals.get('temperature_c', 37)
        o2 = vitals.get('oxygen_saturation', 98)
        hr = vitals.get('heart_rate', 80)
        bp_sys = vitals.get('blood_pressure_systolic', 120)
        
        wbc = lab_values.get('wbc', 0)
        crp = lab_values.get('crp', 0)
        
        # FIXED RULES FOR DIAGNOSIS
        diagnosis = "Unknown condition"
        confidence = 0.5
        risk = "LOW"
        
        # Rule 1: Pneumonia (most specific)
        if (wbc > 15 or crp > 50) and any('pneumonia' in f.lower() or 'infiltrate' in f.lower() for f in xray_findings):
            diagnosis = "Bacterial pneumonia"
            confidence = 0.9
            risk = "HIGH" if o2 < 92 or age > 65 else "MODERATE"
        
        # Rule 2: Sepsis without clear source
        elif wbc > 15 or crp > 100 or temp > 38.5:
            diagnosis = "Sepsis, source unclear"
            confidence = 0.8
            risk = "HIGH" if temp > 39 or o2 < 94 else "MODERATE"
        
        # Rule 3: Heart failure
        elif any('cardiomegaly' in f.lower() or 'effusion' in f.lower() for f in xray_findings) and bp_sys > 140:
            diagnosis = "Congestive heart failure"
            confidence = 0.85
            risk = "MODERATE" if age > 65 else "LOW"
        
        # Rule 4: Respiratory infection
        elif temp > 37.5 and (o2 < 95 or any('consolidation' in f.lower() for f in xray_findings)):
            diagnosis = "Lower respiratory tract infection"
            confidence = 0.75
            risk = "MODERATE"
        
        # Rule 5: Undifferentiated if no clear pattern
        else:
            diagnosis = "Undifferentiated illness requiring further workup"
            confidence = 0.5
            risk = "LOW" if all([temp < 38, o2 > 95, wbc < 12]) else "MODERATE"
        
        # FIXED DISPOSITION RULES
        if risk == "HIGH" or o2 < 90:
            disposition = "Admit to ICU"
        elif risk == "MODERATE" or age > 70:
            disposition = "Admit to medical floor"
        else:
            disposition = "Observe in ER"
        
        # FIXED COST CALCULATION
        base_cost = {
            "HIGH": 25000,
            "MODERATE": 12000,
            "LOW": 5000
        }[risk]
        
        # Age adjustment
        if age > 65:
            base_cost *= 1.3
        
        total_cost = int(base_cost + (age * 100))
        
        return {
            'diagnosis': diagnosis,
            'confidence': confidence,
            'risk': risk,
            'disposition': disposition,
            'total_cost': total_cost,
            'reasoning': f"Based on fixed rules: WBC={wbc}, CRP={crp}, O2={o2}%, Age={age}",
            'consistency_hash': input_hash[:8]  # Show that same inputs = same hash
        }

# Example usage:
if __name__ == "__main__":
    # Test with same inputs multiple times
    test_patient = {
        'age': 58,
        'vitals': {
            'temperature_c': 38.7,
            'oxygen_saturation': 94,
            'heart_rate': 101
        }
    }
    
    test_labs = {'wbc': 19.0, 'crp': 82.9}
    test_xray = ['Infiltrates present', 'Pneumonia detected']
    
    # Run 3 times - should get SAME result
    for i in range(3):
        result = DeterministicAnalyzer.analyze_patient(test_patient, test_labs, test_xray)
        print(f"Run {i+1}: {result['diagnosis']} (Risk: {result['risk']}) - Hash: {result['consistency_hash']}")
