"""
Fixed AI Patient View - Generates comprehensive patient-friendly explanations
"""
from typing import Dict
import asyncio

async def generate_ai_patient_view(analysis_results: Dict) -> Dict:
    """
    Generate comprehensive patient view with all features
    """
    # Extract data
    consensus = analysis_results.get('consensus', {})
    patient_data = analysis_results.get('patient_data') or analysis_results.get('patient', {})
    detailed_findings = analysis_results.get('detailed_findings', {})
    
    # Get key information
    diagnosis = consensus.get('primary_diagnosis', 'Unknown condition')
    disposition = consensus.get('disposition', 'Follow up with your doctor')
    confidence = consensus.get('confidence_level', 'MODERATE')
    key_interventions = consensus.get('key_interventions', [])
    
    # Get patient vitals
    vitals = patient_data.get('vitals', {})
    age = patient_data.get('age', 0)
    
    # Determine severity based on multiple factors
    is_icu = 'ICU' in disposition
    is_admission = 'Admit' in disposition
    is_critical = is_icu or confidence == 'CRITICAL' or vitals.get('oxygen_saturation', 100) < 90
    
    # Generate emergency alert
    alert_data = {
        "show_alert": is_critical or is_icu,
        "severity": "critical" if is_critical else "high" if is_admission else "moderate",
        "title": f"{'URGENT: ' if is_critical else ''}Medical Attention Required",
        "message": f"You have been diagnosed with {diagnosis}. {'Immediate hospital care is needed.' if is_critical else 'Please follow the recommended treatment plan.'}",
        "urgency_reasons": []
    }
    
    # Add urgency reasons
    if is_critical:
        if vitals.get('oxygen_saturation', 100) < 90:
            alert_data['urgency_reasons'].append(f"⚠️ Low oxygen level: {vitals.get('oxygen_saturation')}%")
        if 'sepsis' in diagnosis.lower():
            alert_data['urgency_reasons'].append("⚠️ Signs of severe infection (sepsis)")
        if is_icu:
            alert_data['urgency_reasons'].append("⚠️ Condition requires intensive care monitoring")
    
    # Add diagnosis-specific reasons
    alert_data['urgency_reasons'].append(f"Diagnosis: {diagnosis}")
    alert_data['urgency_reasons'].extend(key_interventions[:2])
    
    # Generate admission information
    admission_data = {
        "needs_admission": is_admission or is_icu,
        "admission_type": "ICU" if is_icu else "Hospital Ward" if is_admission else "Outpatient",
        "expected_stay": "5-7 days" if is_icu else "3-5 days" if is_admission else "No admission needed",
        "reasons": [],
        "what_to_expect": [],
        "daily_plan": {}
    }
    
    if is_admission or is_icu:
        # Add admission reasons
        admission_data['reasons'] = [
            f"Your condition ({diagnosis}) requires hospital care",
            "You need IV medications and close monitoring",
            "Your vital signs need continuous observation"
        ]
        
        # What to expect
        admission_data['what_to_expect'] = [
            "Regular vital sign checks every 4-6 hours",
            "IV medications to treat your condition",
            "Blood tests to monitor your progress",
            "Imaging studies if needed"
        ]
        
        # Daily plan
        admission_data['daily_plan'] = {
            "Day 1": ["Admission and initial treatment", "Start IV antibiotics", "Continuous monitoring"],
            "Day 2-3": ["Continue treatment", "Monitor response", "Adjust medications as needed"],
            "Day 4+": ["Evaluate for discharge", "Transition to oral medications if improving"]
        }
    
    # Generate cost estimates
    base_cost = 20000 if is_icu else 12000 if is_admission else 2500
    cost_data = {
        "total_estimated": base_cost,
        "breakdown": {
            "Room and nursing care": base_cost * 0.4,
            "Medications": base_cost * 0.2,
            "Laboratory tests": base_cost * 0.15,
            "Imaging studies": base_cost * 0.15,
            "Physician services": base_cost * 0.1
        },
        "insurance_estimate": {
            "with_insurance": base_cost * 0.2,  # Assuming 80% coverage
            "deductible_info": "Subject to your plan's deductible",
            "coverage_note": "Most insurance plans cover 70-80% after deductible"
        },
        "financial_options": [
            "Payment plans available",
            "Financial assistance programs may apply",
            "Discuss with billing department"
        ]
    }
    
    # Generate treatment options
    options_data = {
        "recommended_action": disposition,
        "treatment_approach": f"Standard care protocol for {diagnosis}",
        "alternatives": [],
        "questions_for_doctor": [
            f"What are the specific treatments for {diagnosis}?",
            "What are the expected outcomes and timeline?",
            "Are there any alternative treatment options?",
            "What are the potential side effects?",
            "When can I return to normal activities?"
        ],
        "red_flags": [
            "Worsening shortness of breath",
            "Chest pain or pressure",
            "High fever over 103°F",
            "Confusion or altered mental state",
            "Severe weakness or dizziness"
        ]
    }
    
    # Add specific red flags based on diagnosis
    if 'pneumonia' in diagnosis.lower():
        options_data['red_flags'].insert(0, "Coughing up blood")
    if 'sepsis' in diagnosis.lower():
        options_data['red_flags'].insert(0, "Rapid heart rate with low blood pressure")
    
    # Compile final view
    return {
        "success": True,
        "alert": alert_data,
        "admission": admission_data,
        "cost": cost_data,
        "options": options_data,
        "summary": {
            "diagnosis": diagnosis,
            "severity": confidence,
            "key_findings": detailed_findings.get('lab', {}).get('patterns', []),
            "next_steps": key_interventions[:3] if key_interventions else ["Follow treatment plan"]
        }
    }
