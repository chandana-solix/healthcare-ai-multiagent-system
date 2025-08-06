"""
Unified Cost Estimation Module
Ensures consistent cost calculations across all views
"""

def calculate_hospital_cost(risk_level: str, diagnosis: str, age: int, los_days: int) -> dict:
    """
    Calculate hospital costs consistently across the system
    
    Args:
        risk_level: CRITICAL, HIGH, MODERATE, or LOW
        diagnosis: Primary diagnosis
        age: Patient age
        los_days: Length of stay in days
    
    Returns:
        Dictionary with cost breakdown
    """
    
    # Base daily rates by risk level
    daily_rates = {
        "CRITICAL": 3500,
        "HIGH": 2500,
        "MODERATE": 1500,
        "LOW": 800
    }
    
    # Get base daily rate
    daily_rate = daily_rates.get(risk_level, 1500)
    
    # Calculate base cost
    base_cost = daily_rate * los_days
    
    # Diagnosis-specific additions (fixed amounts, not multipliers)
    diagnosis_costs = {
        "pneumonia": 2000,  # Antibiotics, respiratory therapy
        "sepsis": 3500,     # Intensive monitoring, IV antibiotics
        "heart failure": 2500,  # Cardiac medications, monitoring
        "copd": 1500,       # Respiratory treatments
        "bronchitis": 800   # Basic respiratory care
    }
    
    # Find matching diagnosis cost
    diagnosis_add = 0
    diagnosis_lower = diagnosis.lower()
    for condition, cost in diagnosis_costs.items():
        if condition in diagnosis_lower:
            diagnosis_add = cost
            break
    
    # Age adjustments (smaller than before)
    age_multiplier = 1.0
    if age > 75:
        age_multiplier = 1.15  # 15% increase for elderly
    elif age > 65:
        age_multiplier = 1.10  # 10% increase
    elif age < 18:
        age_multiplier = 1.10  # 10% increase for pediatric
    
    # Calculate components
    room_and_board = base_cost
    diagnosis_specific = diagnosis_add
    age_adjusted_total = int((room_and_board + diagnosis_specific) * age_multiplier)
    
    # Insurance estimate (typical 70-80% coverage)
    insurance_coverage = 0.75  # 75% coverage
    patient_responsibility = int(age_adjusted_total * (1 - insurance_coverage))
    
    return {
        "total_estimated": age_adjusted_total,
        "breakdown": {
            f"Hospital Care ({los_days} days @ ${daily_rate}/day)": room_and_board,
            f"{diagnosis.split()[0]} Treatment": diagnosis_specific,
            "Tests & Monitoring": int(base_cost * 0.3)  # 30% of base for tests
        },
        "insurance_estimate": {
            "with_insurance": patient_responsibility,
            "coverage_note": f"Typical insurance covers ~{int(insurance_coverage*100)}%"
        },
        "daily_rate": daily_rate,
        "length_of_stay": los_days
    }

def estimate_length_of_stay(risk_level: str, diagnosis: str) -> int:
    """
    Estimate length of stay based on risk and diagnosis
    """
    # Base LOS by risk
    base_los = {
        "CRITICAL": 7,
        "HIGH": 5,
        "MODERATE": 3,
        "LOW": 1
    }
    
    los = base_los.get(risk_level, 3)
    
    # Adjust for specific conditions
    if "sepsis" in diagnosis.lower() and risk_level == "CRITICAL":
        los = 10
    elif "pneumonia" in diagnosis.lower() and risk_level == "HIGH":
        los = 6
    
    return los
