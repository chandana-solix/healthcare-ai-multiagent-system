# Test Data Setup Guide

## 📁 Required Test Data

To test the Healthcare AI System, you need:

1. **Patient Demographics** (JSON) - ✅ Already included in `/test_patients/`
2. **Chest X-ray Images** - Need to provide
3. **Lab Report Images** - Need to provide

## 🔍 Where to Get Test Data:

### Option 1: Public Datasets
- **NIH Chest X-rays**: https://www.kaggle.com/datasets/nih-chest-xrays/data
- **MIMIC-CXR**: https://physionet.org/content/mimic-cxr/2.0.0/

### Option 2: Synthetic Data
- Generate fake lab reports using online templates
- Use "normal chest x-ray" from Google Images (for demo only)

### Option 3: Request from Team
Contact the development team for sample test data package.

## 📂 Expected Folder Structure:
```
test_data/
├── xrays/
│   ├── normal_chest.jpg
│   ├── pneumonia_case.jpg
│   └── critical_case.jpg
└── lab_reports/
    ├── normal_labs.jpg
    ├── infection_labs.jpg
    └── critical_labs.jpg
```

## 🚀 Quick Test:
1. Use any chest X-ray image
2. Use any lab report with visible numbers
3. Use JSON files from `/test_patients/`

The AI will analyze whatever images you provide!
