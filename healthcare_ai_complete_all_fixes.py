#!/usr/bin/env python3
"""
Healthcare Multi-Agent System - Medical AI Models
Includes TorchXRayVision for X-ray analysis and EasyOCR for lab extraction
"""

import os
import sys
import re
import numpy as np
from typing import Dict, List, Optional, Any
import traceback

# Image processing
from PIL import Image

# ============= REAL MEDICAL AI MODELS =============

# 1. TorchXRayVision for chest X-rays
try:
    import torch
    import torchxrayvision as xrv
    XRAY_AI_AVAILABLE = True
    print("✅ TorchXRayVision loaded - Real X-ray AI available!")
except Exception as e:
    XRAY_AI_AVAILABLE = False
    print(f"⚠️ TorchXRayVision not available: {e}")

# 2. EasyOCR for lab report text extraction
try:
    import easyocr
    OCR_AVAILABLE = True
    print("✅ EasyOCR loaded - Real lab value extraction available!")
except:
    OCR_AVAILABLE = False
    print("⚠️ EasyOCR not available")

print("="*60)

# ============= MEDICAL AI MODEL MANAGERS =============

class MedicalAIModels:
    """Centralized manager for all medical AI models"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            self.initialize_models()
            self.initialized = True
    
    def initialize_models(self):
        """Initialize all AI models once"""
        # 1. X-ray model
        if XRAY_AI_AVAILABLE:
            try:
                print("Loading TorchXRayVision model...")
                self.xray_model = xrv.models.DenseNet(weights="densenet121-res224-all")
                self.xray_model.eval()
                print("✅ X-ray model loaded successfully")
            except Exception as e:
                print(f"❌ Error loading X-ray model: {e}")
                self.xray_model = None
        else:
            self.xray_model = None
        
        # 2. OCR reader
        if OCR_AVAILABLE:
            try:
                print("Initializing EasyOCR...")
                self.ocr_reader = easyocr.Reader(['en'], gpu=False)
                print("✅ OCR initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing OCR: {e}")
                self.ocr_reader = None
        else:
            self.ocr_reader = None

# Create singleton instance
ai_models = MedicalAIModels()

# ============= FILE ANALYZER WITH REAL AI =============

class FileAnalyzer:
    """Analyze medical files using real AI models"""
    
    @staticmethod
    def analyze_xray_image(image_path: str) -> Dict[str, Any]:
        """Analyze chest X-ray using TorchXRayVision"""
        
        if not XRAY_AI_AVAILABLE or not ai_models.xray_model:
            print("[X-ray] Using fallback analysis (AI not available)")
            return FileAnalyzer._mock_xray_analysis()
        
        try:
            # Load and preprocess image
            img = Image.open(image_path).convert('RGB')
            img = np.array(img)
            
            # TorchXRayVision expects grayscale
            if len(img.shape) == 3:
                img = img.mean(2)
            
            # Resize to 224x224 as expected by model
            from skimage.transform import resize
            img = resize(img, (224, 224), preserve_range=True)
            
            # Normalize
            img = xrv.datasets.normalize(img, 255)
            
            # Add batch and channel dimensions
            img = torch.from_numpy(img).unsqueeze(0).unsqueeze(0).float()
            
            # Get predictions
            with torch.no_grad():
                outputs = ai_models.xray_model(img)
            
            # Convert outputs to probabilities
            probs = torch.sigmoid(outputs[0]).numpy()
            
            # Get pathology names
            pathologies = ai_models.xray_model.pathologies
            
            # Create findings
            findings = []
            patterns = {}
            ai_predictions = {}
            
            for i, pathology in enumerate(pathologies):
                prob = float(probs[i])
                ai_predictions[pathology] = round(prob, 3)
                
                # Consider positive if probability > 0.5
                if prob > 0.5:
                    findings.append(f"{pathology} detected (confidence: {prob:.1%})")
                    patterns[pathology.lower()] = True
            
            # Generate impression
            if 'Pneumonia' in pathologies and probs[pathologies.index('Pneumonia')] > 0.5:
                impression = "Findings consistent with pneumonia"
            elif 'Consolidation' in pathologies and probs[pathologies.index('Consolidation')] > 0.5:
                impression = "Consolidation present"
            elif any(prob > 0.5 for prob in probs):
                impression = "Abnormal findings detected"
            else:
                impression = "No acute cardiopulmonary process"
            
            return {
                'findings': findings if findings else ['No significant abnormalities'],
                'patterns': patterns,
                'impression': impression,
                'ai_predictions': ai_predictions,
                'ai_model': 'TorchXRayVision DenseNet121'
            }
            
        except Exception as e:
            print(f"[X-ray] Error in AI analysis: {e}")
            traceback.print_exc()
            return FileAnalyzer._mock_xray_analysis()
    
    @staticmethod
    def analyze_lab_image(image_path: str) -> Dict[str, float]:
        """Extract lab values using OCR"""
        
        if not OCR_AVAILABLE or not ai_models.ocr_reader:
            print("[Lab] Using fallback values (OCR not available)")
            return FileAnalyzer._mock_lab_values()
        
        try:
            # Run OCR
            result = ai_models.ocr_reader.readtext(image_path)
            
            # Extract text
            full_text = ' '.join([item[1] for item in result])
            lines = [item[1] for item in result]
            
            print(f"[OCR] Extracted {len(lines)} text segments")
            
            # Parse lab values
            lab_values = {}
            
            # Common lab test patterns
            patterns = {
                'wbc': r'(?:WBC|White\s*Blood|Leukocytes?)\s*[:=]?\s*(\d+\.?\d*)',
                'hemoglobin': r'(?:Hgb|Hemoglobin|HGB)\s*[:=]?\s*(\d+\.?\d*)',
                'platelets': r'(?:PLT|Platelets?)\s*[:=]?\s*(\d+)',
                'creatinine': r'(?:Creat|Creatinine|CREAT)\s*[:=]?\s*(\d+\.?\d*)',
                'bun': r'(?:BUN|Urea)\s*[:=]?\s*(\d+\.?\d*)',
                'glucose': r'(?:Glucose|GLU|Blood\s*Sugar)\s*[:=]?\s*(\d+)',
                'sodium': r'(?:Na|Sodium)\s*[:=]?\s*(\d+)',
                'potassium': r'(?:K|Potassium)\s*[:=]?\s*(\d+\.?\d*)',
                'chloride': r'(?:Cl|Chloride)\s*[:=]?\s*(\d+)',
                'crp': r'(?:CRP|C-Reactive)\s*[:=]?\s*(\d+\.?\d*)',
                'lactate': r'(?:Lactate|Lactic)\s*[:=]?\s*(\d+\.?\d*)',
                'troponin': r'(?:Troponin|TROP)\s*[:=]?\s*(\d+\.?\d*)',
                'bnp': r'(?:BNP|Brain\s*Natriuretic)\s*[:=]?\s*(\d+)',
                'procalcitonin': r'(?:PCT|Procalcitonin)\s*[:=]?\s*(\d+\.?\d*)'
            }
            
            # Search in full text and individual lines
            for test_name, pattern in patterns.items():
                # Try full text first
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    try:
                        value = float(match.group(1))
                        lab_values[test_name] = value
                        print(f"[OCR] Found {test_name}: {value}")
                    except:
                        pass
                else:
                    # Try line by line
                    for line in lines:
                        match = re.search(pattern, line, re.IGNORECASE)
                        if match:
                            try:
                                value = float(match.group(1))
                                lab_values[test_name] = value
                                print(f"[OCR] Found {test_name}: {value}")
                                break
                            except:
                                pass
            
            # If we found some values, return them; otherwise use mock data
            if len(lab_values) > 5:  # At least 5 values extracted
                print(f"[OCR] Successfully extracted {len(lab_values)} lab values")
                return lab_values
            else:
                print(f"[OCR] Only found {len(lab_values)} values, using mock data")
                return FileAnalyzer._mock_lab_values()
                
        except Exception as e:
            print(f"[Lab] Error in OCR analysis: {e}")
            return FileAnalyzer._mock_lab_values()
    
    @staticmethod
    def _mock_xray_analysis() -> Dict[str, Any]:
        """Fallback X-ray analysis when AI not available"""
        return {
            'findings': ['Consolidation in right lower lobe', 'No pleural effusion'],
            'patterns': {'pneumonia': True, 'consolidation': True},
            'impression': 'Findings consistent with right lower lobe pneumonia',
            'ai_predictions': {'Pneumonia': 0.82, 'Consolidation': 0.76},
            'ai_model': 'Mock (AI not available)'
        }
    
    @staticmethod
    def _mock_lab_values() -> Dict[str, float]:
        """Fallback lab values when OCR not available"""
        return {
            'wbc': 15.8,
            'hemoglobin': 12.1,
            'platelets': 245,
            'creatinine': 1.8,
            'bun': 35,
            'glucose': 185,
            'crp': 125,
            'procalcitonin': 3.2,
            'lactate': 2.8,
            'sodium': 138,
            'potassium': 4.2,
            'chloride': 102,
            'bnp': 450,
            'troponin': 0.02
        }
