#!/usr/bin/env python3
"""Test if ML models load correctly"""

print("Testing ML Models...\n")

# Test 1: PyTorch
try:
    import torch
    print("✅ PyTorch loaded successfully")
    print(f"   Version: {torch.__version__}")
except Exception as e:
    print(f"❌ PyTorch failed: {e}")

# Test 2: TorchXRayVision
try:
    import torchxrayvision as xrv
    print("✅ TorchXRayVision loaded successfully")
except Exception as e:
    print(f"❌ TorchXRayVision failed: {e}")

# Test 3: EasyOCR
try:
    import easyocr
    print("✅ EasyOCR loaded successfully")
except Exception as e:
    print(f"❌ EasyOCR failed: {e}")

# Test 4: Load the actual models
try:
    from healthcare_ai_complete_all_fixes import ai_models
    print("\n✅ AI models module loaded successfully")
    
    if ai_models.xray_model:
        print("✅ X-ray model initialized")
    else:
        print("⚠️  X-ray model not initialized")
        
    if ai_models.ocr_reader:
        print("✅ OCR reader initialized")
    else:
        print("⚠️  OCR reader not initialized")
        
except Exception as e:
    print(f"\n❌ Error loading AI models: {e}")

print("\n🏁 Test complete!")
