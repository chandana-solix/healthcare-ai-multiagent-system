"""
Application configuration
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

# API Configuration
API_TITLE = "Healthcare Multi-Agent System"
API_VERSION = "1.0.0"
API_DESCRIPTION = "AI-powered clinical decision support system"

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# AI Model Configuration
ENABLE_XRAY_AI = os.getenv("ENABLE_XRAY_AI", "True").lower() == "true"
ENABLE_OCR = os.getenv("ENABLE_OCR", "True").lower() == "true"

# Medical Thresholds (can be customized)
CRITICAL_THRESHOLDS = {
    "wbc": {"low": 2.0, "high": 20.0},
    "creatinine": {"high": 3.0},
    "potassium": {"low": 2.5, "high": 6.5},
    "glucose": {"low": 40, "high": 500},
    "crp": {"high": 100.0}
}

# Risk Scoring Weights
RISK_WEIGHTS = {
    "sirs_score": 2.0,
    "curb65_score": 2.5,
    "age_factor": 1.5,
    "comorbidity": 1.0
}

# Database Configuration (optional)
USE_DATABASE = os.getenv("USE_DATABASE", "False").lower() == "true"
DATABASE_PATH = os.getenv("DATABASE_PATH", "healthcare.db")
