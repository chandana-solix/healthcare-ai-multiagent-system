# Sample Test Files for Healthcare AI System

This directory contains sample files for testing the Healthcare AI Multi-Agent System:

## 1. Demographics File (JSON)
- **File**: `sample_demographics.json`
- **Description**: Patient demographic information including vitals
- **Usage**: Upload this file in the "Demographics" section

## 2. Lab Report (Image)
- **File**: Use any image file as a placeholder
- **Description**: The system will analyze it as a lab report
- **Note**: With EasyOCR enabled, it will attempt to extract text from real lab reports

## 3. X-Ray Image
- **File**: Use any chest X-ray image or placeholder
- **Description**: The system will analyze it using TorchXRayVision if available
- **Note**: For best results, use actual chest X-ray images

## Testing Instructions:
1. Download the sample_demographics.json file
2. Upload it along with any image files for lab and X-ray
3. Click "Analyze" to see the multi-agent system in action

The system will:
- Extract patient information from demographics
- Analyze lab values (simulated or OCR-extracted)
- Process X-ray findings
- Calculate risk scores
- Make clinical decisions
- Build consensus among agents
