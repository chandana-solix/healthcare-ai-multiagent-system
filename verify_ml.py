#!/usr/bin/env python3
"""Verify ML models are actually being used"""

from healthcare_ai_complete_all_fixes import ai_models, FileAnalyzer
import numpy as np

print("🔍 VERIFYING ML MODELS ARE ACTIVE\n")

# 1. Check if models are loaded
print("1. Model Loading Status:")
print(f"   X-ray Model Loaded: {ai_models.xray_model is not None}")
print(f"   OCR Reader Loaded: {ai_models.ocr_reader is not None}")

if ai_models.xray_model:
    print(f"   Model Type: {type(ai_models.xray_model)}")
    print(f"   Model Location: {'GPU/MPS' if next(ai_models.xray_model.parameters()).is_mps else 'CPU'}")

# 2. Test with a fake X-ray
print("\n2. Testing X-ray Analysis:")
# Create a random image
test_image = np.random.rand(224, 224, 3) * 255
from PIL import Image
img = Image.fromarray(test_image.astype('uint8'))
img.save('/tmp/test_xray.jpg')

# Analyze it
result = FileAnalyzer.analyze_xray_image('/tmp/test_xray.jpg')
print(f"   Number of conditions detected: {len(result['ai_predictions'])}")
print(f"   Using model: {result['ai_model']}")
print(f"   Sample predictions: {list(result['ai_predictions'].items())[:3]}")

# 3. Verify it's not mock data
print("\n3. Checking if results are dynamic:")
is_mock = result['ai_model'] == 'Mock (AI not available)'
print(f"   Using mock data: {is_mock}")
print(f"   Results are from: {'MOCK DATA' if is_mock else 'REAL AI MODEL'}")

print("\n✅ VERIFICATION COMPLETE!")
