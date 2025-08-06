"""
Hybrid Medical Analysis System - Combines AI intelligence with deterministic consistency
"""
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
from utils.cost_calculator import calculate_hospital_cost, estimate_length_of_stay

class HybridMedicalAnalyzer:
    """
    Combines AI analysis with consistency rules and caching
    """
    
    def __init__(self, cache_file="analysis_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """Load analysis cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def _generate_cache_key(self, patient_data: Dict, files_hash: str) -> str:
        """Generate consistent cache key for patient + date"""
        # Include patient ID, age, chief complaint, and date
        key_data = {
            'patient_id': patient_data.get('patient_id'),
            'age': patient_data.get('age'),
            'complaint': patient_data.get('chief_complaint'),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'files': files_hash
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    def analyze_with_consistency(self, 
                                patient_data: Dict, 
                                ai_analysis: Dict,
                                lab_values: Dict,
                                xray_findings: list) -> Dict:
        """
        Wrapper around AI analysis that adds consistency
        """
        # Generate cache key
        files_hash = hashlib.md5(f"{lab_values}{xray_findings}".encode()).hexdigest()[:8]
        cache_key = self._generate_cache_key(patient_data, files_hash)
        
        # Check cache first (24-hour validity)
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            cache_time = datetime.fromisoformat(cached['timestamp'])
            if datetime.now() - cache_time < timedelta(hours=24):
                print(f"🔄 Using cached analysis for consistency")
                return cached['analysis']
        
        # Get AI analysis results
        diagnosis = ai_analysis.get('consensus', {}).get('primary_diagnosis', 'Unknown')
        risk = ai_analysis.get('detailed_findings', {}).get('risk', {}).get('overall_risk', 'LOW')
        confidence = ai_analysis.get('consensus', {}).get('confidence_level', 'LOW')
        
        # Apply consistency rules
        enhanced_analysis = self._apply_consistency_rules(
            patient_data, 
            ai_analysis, 
            lab_values, 
            xray_findings
        )
        
        # Add confidence indicators
        enhanced_analysis['confidence_indicators'] = {
            'ai_confidence': confidence,
            'agent_agreement': self._calculate_agreement(ai_analysis),
            'data_completeness': self._check_data_completeness(lab_values, xray_findings),
            'consistency_applied': True
        }
        
        # Cache the result
        self.cache[cache_key] = {
            'timestamp': datetime.now().isoformat(),
            'analysis': enhanced_analysis
        }
        self._save_cache()
        
        return enhanced_analysis
    
    def _apply_consistency_rules(self, patient_data, ai_analysis, lab_values, xray_findings):
        """Apply medical rules to ensure consistency"""
        
        # Extract key values
        age = patient_data.get('age', 0)
        vitals = patient_data.get('vitals', {})
        o2 = vitals.get('oxygen_saturation', 98)
        temp_c = vitals.get('temperature_c', 37)
        hr = vitals.get('heart_rate', 80)
        
        # Get AI results
        ai_diagnosis = ai_analysis.get('consensus', {}).get('primary_diagnosis', 'Unknown')
        ai_risk = ai_analysis.get('detailed_findings', {}).get('risk', {}).get('overall_risk', 'LOW')
        
        # Initialize with AI results
        final_diagnosis = ai_diagnosis
        final_risk = ai_risk
        override_reason = None
        
        # CRITICAL OVERRIDES - Fixed rules for safety
        
        # Rule 1: Critical oxygen levels
        if o2 < 88:
            final_risk = "CRITICAL"
            override_reason = f"Critical oxygen level: {o2}%"
        elif o2 < 92 and ai_risk == "LOW":
            final_risk = "HIGH"
            override_reason = f"Low oxygen ({o2}%) requires high risk classification"
        
        # Rule 2: Severe infection markers
        wbc = lab_values.get('wbc', 0)
        crp = lab_values.get('crp', 0)
        if (wbc > 20 or crp > 100) and ai_risk == "LOW":
            final_risk = "HIGH"
            override_reason = "Severe infection markers present"
        
        # Rule 3: Elderly with fever
        if age > 65 and temp_c > 38.5 and ai_risk == "LOW":
            final_risk = "MODERATE"
            override_reason = "Elderly patient with fever"
        
        # Rule 4: Diagnosis validation
        if "pneumonia" in ai_diagnosis.lower():
            # Pneumonia must have supporting evidence
            has_xray_evidence = any('pneumonia' in f.lower() or 'infiltrate' in f.lower() 
                                  for f in xray_findings)
            has_lab_evidence = wbc > 12 or crp > 30
            
            if not (has_xray_evidence or has_lab_evidence):
                final_diagnosis = "Suspected pneumonia - requires confirmation"
                override_reason = "Insufficient evidence for definitive pneumonia diagnosis"
        
        # Fixed disposition based on validated risk
        disposition_map = {
            "CRITICAL": "Admit to ICU",
            "HIGH": "Admit to ICU" if o2 < 92 else "Admit to step-down unit",
            "MODERATE": "Admit to medical floor",
            "LOW": "Observe in ER" if any([temp_c > 38, o2 < 95]) else "Discharge with follow-up"
        }
        
        final_disposition = disposition_map.get(final_risk, "Admit to medical floor")
        
        # Calculate costs using unified calculator
        los = estimate_length_of_stay(final_risk, final_diagnosis)
        cost_data = calculate_hospital_cost(final_risk, final_diagnosis, age, los)
        
        return {
            'diagnosis': final_diagnosis,
            'risk_level': final_risk,
            'disposition': final_disposition,
            'estimated_cost': cost_data['total_estimated'],
            'cost_breakdown': cost_data['breakdown'],
            'insurance_estimate': cost_data['insurance_estimate'],
            'length_of_stay': los,
            'override_applied': override_reason is not None,
            'override_reason': override_reason,
            'ai_original': {
                'diagnosis': ai_diagnosis,
                'risk': ai_risk
            }
        }
    
    def _calculate_agreement(self, ai_analysis) -> str:
        """Calculate agent agreement level"""
        # Extract from consensus builder
        consensus = ai_analysis.get('consensus', {})
        if 'confidence_level' in consensus:
            if 'HIGH' in consensus['confidence_level']:
                return "Strong (>80%)"
            elif 'LOW' in consensus['confidence_level']:
                return "Weak (<50%)"
        return "Moderate (50-80%)"
    
    def _check_data_completeness(self, lab_values, xray_findings) -> str:
        """Check if we have complete data"""
        lab_count = len([v for v in lab_values.values() if v is not None])
        xray_count = len(xray_findings)
        
        if lab_count > 10 and xray_count > 2:
            return "Complete"
        elif lab_count > 5 or xray_count > 0:
            return "Partial"
        else:
            return "Limited"

    def generate_patient_explanation(self, analysis: Dict) -> Dict:
        """Generate patient-friendly explanation"""
        diagnosis = analysis['diagnosis']
        risk = analysis['risk_level']
        override = analysis.get('override_applied', False)
        
        explanation = {
            'summary': f"Based on your test results, you have been diagnosed with {diagnosis}.",
            'confidence': f"Diagnostic confidence: {analysis['confidence_indicators']['ai_confidence']}",
            'why_this_diagnosis': []
        }
        
        # Add reasoning
        if risk == "CRITICAL":
            explanation['why_this_diagnosis'].append("Your vital signs show critical values requiring immediate attention")
        elif risk == "HIGH":
            explanation['why_this_diagnosis'].append("Your test results indicate significant abnormalities")
        
        if override:
            explanation['why_this_diagnosis'].append(f"Safety override applied: {analysis['override_reason']}")
        
        explanation['consistency_note'] = (
            "This analysis will remain consistent if you check again today. "
            "New test results or symptoms may change the assessment."
        )
        
        return explanation
