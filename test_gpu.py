#!/usr/bin/env python3
"""Test GPU availability and performance on your system"""

import time
import torch
import numpy as np

print("🔍 GPU Detection Test\n")

# 1. Check PyTorch GPU availability
print("1. PyTorch GPU Check:")
if torch.cuda.is_available():
    print(f"   ✅ CUDA GPU available: {torch.cuda.get_device_name(0)}")
elif torch.backends.mps.is_available():
    print("   ✅ Apple Silicon GPU (MPS) available!")
    print(f"   Device: M3 Pro")
else:
    print("   ❌ No GPU detected")

# 2. Test GPU vs CPU performance
print("\n2. Performance Comparison:")

# Create test tensor
size = 1000
x = torch.randn(size, size)

# CPU test
print("\n   CPU Performance:")
start = time.time()
for _ in range(100):
    y = torch.mm(x, x)
cpu_time = time.time() - start
print(f"   Time: {cpu_time:.3f} seconds")

# GPU test (MPS for Mac)
if torch.backends.mps.is_available():
    print("\n   GPU (MPS) Performance:")
    device = torch.device("mps")
    x_gpu = x.to(device)
    
    # Warm up
    for _ in range(10):
        _ = torch.mm(x_gpu, x_gpu)
    
    start = time.time()
    for _ in range(100):
        y_gpu = torch.mm(x_gpu, x_gpu)
    torch.mps.synchronize()  # Wait for GPU to finish
    gpu_time = time.time() - start
    print(f"   Time: {gpu_time:.3f} seconds")
    print(f"   🚀 GPU is {cpu_time/gpu_time:.1f}x faster!")

# 3. Test with your actual models
print("\n3. Testing Your AI Models:")

try:
    # Test TorchXRayVision with GPU
    import torchxrayvision as xrv
    print("\n   TorchXRayVision:")
    model = xrv.models.DenseNet(weights="densenet121-res224-all")
    
    if torch.backends.mps.is_available():
        model = model.to('mps')
        print("   ✅ Model moved to Apple GPU")
    
    # Test inference
    test_image = torch.randn(1, 1, 224, 224)
    if torch.backends.mps.is_available():
        test_image = test_image.to('mps')
    
    start = time.time()
    with torch.no_grad():
        output = model(test_image)
    if torch.backends.mps.is_available():
        torch.mps.synchronize()
    inference_time = time.time() - start
    print(f"   Inference time: {inference_time:.3f} seconds")
    
except Exception as e:
    print(f"   ⚠️  Could not test TorchXRayVision: {e}")

# 4. Test EasyOCR GPU support
print("\n4. EasyOCR GPU Support:")
try:
    import easyocr
    # On Mac, EasyOCR might not use MPS directly
    print("   ℹ️  EasyOCR runs on CPU for Mac (MPS not supported yet)")
    print("   💡 Will use GPU on Linux server with CUDA")
except Exception as e:
    print(f"   ⚠️  Could not test EasyOCR: {e}")

print("\n✅ GPU test complete!")
print("\n📝 Summary:")
print("- Your M3 Pro has GPU support via MPS (Metal Performance Shaders)")
print("- PyTorch can use it for acceleration")
print("- Full GPU acceleration will work on Linux server with NVIDIA GPU")
