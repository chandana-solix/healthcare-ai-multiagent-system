"""
Dynamic Agent Explanation Generator
Provides context-aware descriptions for each agent's findings
"""

def get_risk_explanation(risk_data: dict) -> str:
    """
    Generate explanation for risk stratification discrepancies
    """
    overall_risk = risk_data.get('overall_risk', 'UNKNOWN')
    key_scores = risk_data.get('key_scores', {})
    risk_factors = risk_data.get('risk_factors', [])
    
    # Check if clinical scores are low but overall risk is high
    mews = key_scores.get('MEWS', {})
    sirs = key_scores.get('SIRS', {})
    
    mews_low = mews.get('risk', 'LOW') == 'LOW'
    sirs_low = sirs.get('risk', 'LOW') == 'LOW'
    
    if overall_risk in ['HIGH', 'CRITICAL'] and mews_low and sirs_low:
        # Find the overriding factor
        if any('WBC' in factor or 'CRP' in factor for factor in risk_factors):
            # Extract lab values from risk factors
            lab_info = []
            for factor in risk_factors:
                if 'WBC:' in factor:
                    wbc_val = factor.split('WBC:')[1].split(',')[0].strip()
                    lab_info.append(f"WBC {wbc_val}↑")
                if 'CRP:' in factor:
                    crp_val = factor.split('CRP:')[1].split(')')[0].strip()
                    lab_info.append(f"CRP {crp_val}↑")
            
            if lab_info:
                return f"Despite low clinical scores, critical lab values ({', '.join(lab_info)}) indicate severe infection"
        
        elif any('age' in factor.lower() or 'elderly' in factor.lower() for factor in risk_factors):
            age_factor = next((f for f in risk_factors if 'age' in f.lower() or 'elderly' in f.lower()), '')
            return f"Clinical scores low, but {age_factor.lower()} increases risk"
        
        elif any('comorbidity' in factor.lower() for factor in risk_factors):
            conditions = [f for f in risk_factors if 'comorbidity' in f.lower()]
            return f"Low scores, but {len(conditions)} comorbidities elevate risk"
        
        else:
            return "Multiple subtle factors combine to elevate overall risk"
    
    elif overall_risk == 'LOW' and not mews_low:
        return "Elevated scores, but other factors suggest lower risk"
    
    else:
        # Scores align with risk
        return f"Clinical scores consistent with {overall_risk} risk assessment"


def get_lab_explanation(lab_data: dict) -> str:
    """
    Generate explanation for lab findings
    """
    patterns = lab_data.get('patterns', [])
    key_values = lab_data.get('key_values', {})
    abnormal_count = lab_data.get('abnormal_count', 0)
    critical_count = lab_data.get('critical_count', 0)
    
    if critical_count > 0:
        critical_labs = []
        for test, value in key_values.items():
            if value and test in ['wbc', 'crp', 'lactate', 'troponin']:
                if (test == 'wbc' and value > 20) or \
                   (test == 'crp' and value > 100) or \
                   (test == 'lactate' and value > 4):
                    critical_labs.append(f"{test.upper()} {value}")
        
        if critical_labs:
            return f"Critical values: {', '.join(critical_labs[:2])} require immediate attention"
    
    if 'SEVERE_BACTERIAL_INFECTION' in patterns:
        wbc = key_values.get('wbc', 0)
        crp = key_values.get('crp', 0)
        return f"Severe infection markers: WBC {wbc}, CRP {crp}"
    
    elif 'BACTERIAL_INFECTION' in patterns:
        return "Elevated inflammatory markers suggest bacterial infection"
    
    elif 'VIRAL_PATTERN' in patterns:
        return "Lab pattern consistent with viral infection"
    
    elif patterns:
        return f"{patterns[0].replace('_', ' ').title()} pattern detected"
    
    elif abnormal_count > 0:
        return f"{abnormal_count} abnormal values found, monitoring recommended"
    
    else:
        return "All lab values within normal limits"


def get_imaging_explanation(imaging_data: dict) -> str:
    """
    Generate explanation for imaging findings
    """
    impression = imaging_data.get('impression', '')
    key_findings = imaging_data.get('key_findings', [])
    confidence = imaging_data.get('confidence', 0)
    
    # Count significant findings
    significant_findings = []
    for finding in key_findings:
        if 'confidence:' in finding:
            try:
                conf_value = float(finding.split('confidence:')[1].split('%')[0].strip())
                if conf_value > 60:
                    finding_name = finding.split('(')[0].strip()
                    significant_findings.append(finding_name)
            except:
                pass
    
    if 'pneumonia' in impression.lower():
        if significant_findings:
            return f"Pneumonia confirmed with {', '.join(significant_findings[:2])}"
        else:
            return "Pneumonia suspected based on imaging pattern"
    
    elif significant_findings:
        return f"{len(significant_findings)} findings need clinical correlation"
    
    elif 'normal' in impression.lower():
        return "No acute cardiopulmonary process identified"
    
    else:
        return "Subtle findings - correlate with clinical symptoms"


def get_clinical_explanation(clinical_data: dict, risk_level: str) -> str:
    """
    Generate explanation for clinical decisions
    """
    diagnosis = clinical_data.get('primary_diagnosis', 'Unknown')
    confidence = clinical_data.get('confidence', 0)
    medications = clinical_data.get('key_medications', [])
    
    if 'pneumonia' in diagnosis.lower() and confidence > 0.8:
        return f"High confidence in {diagnosis} - antibiotics started"
    elif 'sepsis' in diagnosis.lower():
        return "Sepsis protocol activated - broad spectrum coverage"
    elif confidence > 0.6:
        return f"{diagnosis} likely, empiric treatment started"
    else:
        return f"Working diagnosis: {diagnosis}, monitoring response"


def get_analytics_explanation(los: int, cost: int, risk_level: str, diagnosis: str) -> str:
    """
    Generate explanation for analytics predictions
    """
    if risk_level == 'CRITICAL':
        return f"Extended stay expected due to critical condition"
    elif risk_level == 'HIGH' and 'sepsis' in diagnosis.lower():
        return f"Complex sepsis management requires {los}-day stay"
    elif risk_level == 'HIGH':
        return f"Typical {los}-day stay for severe infection"
    elif los > 5:
        return f"Longer stay due to complexity of care"
    else:
        return f"Standard admission for {risk_level.lower()} risk patient"


def get_consensus_explanation(agreement_pct: int, consensus_data: dict) -> str:
    """
    Generate explanation for consensus level
    """
    dissenting = consensus_data.get('dissenting_opinions', [])
    primary_diagnosis = consensus_data.get('primary_diagnosis', '')
    
    if agreement_pct >= 80:
        return "Strong consensus - all agents agree on approach"
    elif agreement_pct >= 60:
        return "Good agreement with minor variations in approach"
    elif dissenting and 'diagnosis' in str(dissenting):
        return "Agents debated diagnosis - clinical judgment prevailed"
    elif agreement_pct < 50:
        topics = []
        if 'diagnosis' in str(dissenting).lower():
            topics.append('diagnosis')
        if 'disposition' in str(dissenting).lower():
            topics.append('admission level')
        if topics:
            return f"Significant debate on {' and '.join(topics)}"
        else:
            return "Complex case with multiple valid approaches"
    else:
        return "Moderate consensus reached after discussion"
