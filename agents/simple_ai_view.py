"""Simple AI View - Fallback that always works"""

async def generate_ai_patient_view(analysis_results):
    """Generate patient view without AI dependencies"""
    
    consensus = analysis_results.get('consensus', {})
    patient = analysis_results.get('patient', {})
    
    diagnosis = consensus.get('primary_diagnosis', 'Unknown condition')
    disposition = consensus.get('disposition', 'See your doctor')
    confidence = consensus.get('confidence_level', 'MODERATE')
    
    # Determine severity
    is_critical = 'ICU' in disposition or 'CRITICAL' in confidence
    is_admission = 'Admit' in disposition
    
    return {
        "success": True,
        "alert": {
            "show_alert": is_critical,
            "severity": "high" if is_critical else "moderate",
            "title": f"Medical Attention Required - {diagnosis}",
            "message": f"Diagnosis: {diagnosis}. {disposition}",
            "urgency_reasons": [
                f"Diagnosed with {diagnosis}",
                f"Medical team recommends: {disposition}",
                f"Confidence level: {confidence}"
            ]
        },
        "admission": {
            "needs_admission": is_admission,
            "explanation": f"Based on your {diagnosis}, {disposition}",
            "expected_stay": "3-5 days" if is_admission else "Outpatient treatment",
            "reasons": [
                diagnosis,
                disposition
            ]
        },
        "cost": {
            "total_estimated": 15000 if is_critical else 8000 if is_admission else 2000,
            "insurance_estimate": {
                "with_insurance": 3000 if is_critical else 1600 if is_admission else 400,
                "coverage_note": "Typical insurance covers 80%"
            }
        },
        "options": {
            "recommended_action": disposition,
            "questions_for_doctor": [
                f"What is the treatment plan for {diagnosis}?",
                "What are the expected outcomes?",
                "Are there alternative treatments?",
                "What are the risks and side effects?"
            ],
            "red_flags": [
                "Difficulty breathing",
                "Chest pain",
                "High fever",
                "Confusion"
            ]
        }
    }
