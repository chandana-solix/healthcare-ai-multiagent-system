"""
Enhanced Patient View with Consistency - Shows both AI results and consistency checks
"""
from typing import Dict
import asyncio
from agents.fixed_ai_patient_view import generate_ai_patient_view as original_patient_view
from utils.hybrid_analyzer import HybridMedicalAnalyzer

# Initialize hybrid analyzer
hybrid_analyzer = HybridMedicalAnalyzer()

async def generate_ai_patient_view(clinical_data: Dict) -> Dict:
    """
    Generate patient view with CONSISTENCY checking
    """
    # First get the original AI patient view
    original_view = await original_patient_view(clinical_data)
    
    # Extract necessary data for hybrid analysis
    patient_data = clinical_data.get('patient_data') or clinical_data.get('patient', {})
    lab_data = clinical_data.get('detailed_findings', {}).get('lab', {}).get('key_values', {})
    xray_data = clinical_data.get('detailed_findings', {}).get('imaging', {}).get('key_findings', [])
    
    # Run hybrid consistency check
    try:
        hybrid_result = hybrid_analyzer.analyze_with_consistency(
            patient_data,
            clinical_data,
            lab_data,
            xray_data
        )
        
        # Add consistency information to the view
        if hybrid_result.get('override_applied'):
            # Modify alert if critical override
            if 'Critical oxygen' in hybrid_result.get('override_reason', ''):
                original_view['alert']['show_alert'] = True
                original_view['alert']['severity'] = 'critical'
                original_view['alert']['urgency_reasons'].insert(0, 
                    f"⚠️ {hybrid_result['override_reason']}")
            
            # Add consistency note to options
            original_view['options']['consistency_note'] = {
                'title': '🔒 Consistency Check Applied',
                'message': hybrid_result['override_reason'],
                'original_ai': f"AI initially suggested: {hybrid_result['ai_original']['diagnosis']}",
                'confidence': hybrid_result['confidence_indicators']
            }
        
        # Add analysis metadata
        original_view['analysis_metadata'] = {
            'ai_confidence': hybrid_result['confidence_indicators']['ai_confidence'],
            'agent_agreement': hybrid_result['confidence_indicators']['agent_agreement'],
            'data_completeness': hybrid_result['confidence_indicators']['data_completeness'],
            'consistency_applied': hybrid_result['confidence_indicators']['consistency_applied'],
            'analysis_id': hybrid_result.get('consistency_hash', 'N/A')
        }
        
        # Update costs with deterministic calculation
        if 'estimated_cost' in hybrid_result:
            original_view['cost']['total_estimated'] = hybrid_result['estimated_cost']
            original_view['cost']['calculation_method'] = 'Hybrid (AI + Rules)'
        
    except Exception as e:
        print(f"Hybrid analysis error: {e}")
        # Add note that consistency check failed
        original_view['analysis_metadata'] = {
            'consistency_check': 'Failed - using pure AI results',
            'error': str(e)
        }
    
    return original_view

# Additional function to show analysis history
async def get_analysis_history(patient_id: str) -> Dict:
    """
    Get history of analyses for a patient showing consistency
    """
    cache = hybrid_analyzer._load_cache()
    patient_analyses = []
    
    for key, value in cache.items():
        if patient_id in key:
            patient_analyses.append({
                'timestamp': value['timestamp'],
                'diagnosis': value['analysis']['diagnosis'],
                'risk': value['analysis']['risk_level'],
                'consistency_hash': key[:8]
            })
    
    return {
        'patient_id': patient_id,
        'total_analyses': len(patient_analyses),
        'analyses': sorted(patient_analyses, key=lambda x: x['timestamp'], reverse=True)[:5]
    }
