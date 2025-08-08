#!/usr/bin/env python3
"""
Comprehensive System Test for Healthcare AI Multi-Agent System
Run this to verify all components are working correctly
"""

import asyncio
import json
import sys
from pathlib import Path
import aiohttp
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Configuration
BASE_URL = "http://localhost:8000"  # Change for production
TEST_PATIENT_ID = "P00013"

# Test results storage
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def print_header(text):
    print(f"\n{'='*60}")
    print(f"🧪 {text}")
    print('='*60)

def print_test(name, status, message=""):
    icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{icon} {name}: {status} {message}")
    
    if status == "PASS":
        test_results["passed"].append(name)
    elif status == "FAIL":
        test_results["failed"].append((name, message))
    else:
        test_results["warnings"].append((name, message))

async def test_health_endpoint():
    """Test if server is running"""
    print_header("Testing Server Health")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print_test("Server Health Check", "PASS", f"Agents: {data.get('agents', [])}")
                    return True
                else:
                    print_test("Server Health Check", "FAIL", f"Status: {resp.status}")
                    return False
    except Exception as e:
        print_test("Server Health Check", "FAIL", str(e))
        return False

async def test_static_files():
    """Test if static files are served"""
    print_header("Testing Static Files")
    
    endpoints = [
        ("/", "Dashboard HTML"),
        ("/patient", "Patient View HTML"),
        ("/static/dashboard.html", "Dashboard Static"),
        ("/static/patient_view.html", "Patient View Static")
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint, name in endpoints:
            try:
                async with session.get(f"{BASE_URL}{endpoint}") as resp:
                    if resp.status == 200:
                        print_test(f"{name}", "PASS")
                    else:
                        print_test(f"{name}", "FAIL", f"Status: {resp.status}")
            except Exception as e:
                print_test(f"{name}", "FAIL", str(e))

async def test_websocket():
    """Test WebSocket connection"""
    print_header("Testing WebSocket Connection")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(f"{BASE_URL.replace('http', 'ws')}/ws") as ws:
                print_test("WebSocket Connection", "PASS")
                
                # Wait for a message
                try:
                    msg = await asyncio.wait_for(ws.receive(), timeout=2.0)
                    print_test("WebSocket Message Reception", "PASS")
                except asyncio.TimeoutError:
                    print_test("WebSocket Message Reception", "WARN", "No messages received")
                
                await ws.close()
    except Exception as e:
        print_test("WebSocket Connection", "FAIL", str(e))

async def test_patient_analysis():
    """Test the full analysis pipeline"""
    print_header("Testing Patient Analysis Pipeline")
    
    # Get test files
    test_files = {
        "demographics": Path("test_patients") / f"{TEST_PATIENT_ID}_demographics.json",
        "lab": Path("test_patients") / f"{TEST_PATIENT_ID}_lab.jpg",
        "xray": Path("test_patients") / f"{TEST_PATIENT_ID}_xray.jpg"
    }
    
    # Check if test files exist
    for file_type, file_path in test_files.items():
        if not file_path.exists():
            print_test(f"Test File - {file_type}", "FAIL", f"File not found: {file_path}")
            return
        else:
            print_test(f"Test File - {file_type}", "PASS", f"Found: {file_path.name}")
    
    # Run analysis
    try:
        async with aiohttp.ClientSession() as session:
            # Prepare form data
            data = aiohttp.FormData()
            
            with open(test_files["demographics"], 'rb') as f:
                data.add_field('demographics', f, filename='demographics.json')
            with open(test_files["lab"], 'rb') as f:
                data.add_field('lab_report', f, filename='lab.jpg')
            with open(test_files["xray"], 'rb') as f:
                data.add_field('xray', f, filename='xray.jpg')
            
            # Send request
            start_time = time.time()
            async with session.post(f"{BASE_URL}/analyze", data=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    elapsed = time.time() - start_time
                    
                    print_test("Analysis Endpoint", "PASS", f"Completed in {elapsed:.2f}s")
                    
                    # Check result structure
                    required_keys = ['consensus', 'detailed_findings', 'agent_communication']
                    for key in required_keys:
                        if key in result:
                            print_test(f"Result - {key}", "PASS")
                        else:
                            print_test(f"Result - {key}", "FAIL", "Missing in response")
                    
                    return result
                else:
                    print_test("Analysis Endpoint", "FAIL", f"Status: {resp.status}")
                    return None
                    
    except Exception as e:
        print_test("Analysis Endpoint", "FAIL", str(e))
        return None

async def test_patient_view(analysis_results):
    """Test patient view generation"""
    print_header("Testing Patient View Generation")
    
    if not analysis_results:
        print_test("Patient View", "SKIP", "No analysis results available")
        return
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/patient_view",
                json=analysis_results
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print_test("Patient View Endpoint", "PASS")
                    
                    # Check required sections
                    sections = ['alert', 'admission', 'cost', 'options']
                    for section in sections:
                        if section in result:
                            print_test(f"Patient View - {section}", "PASS")
                        else:
                            print_test(f"Patient View - {section}", "FAIL", "Missing section")
                    
                    # Check cost consistency
                    if 'cost' in result and 'total_estimated' in result['cost']:
                        cost = result['cost']['total_estimated']
                        print_test("Cost Calculation", "PASS", f"${cost:,}")
                    
                    return result
                else:
                    print_test("Patient View Endpoint", "FAIL", f"Status: {resp.status}")
                    return None
                    
    except Exception as e:
        print_test("Patient View Endpoint", "FAIL", str(e))
        return None

async def test_agent_components():
    """Test individual agent availability"""
    print_header("Testing Agent Components")
    
    try:
        from agents.intelligent_lab_analyzer import lab_analyzer
        print_test("Lab Analyzer Agent", "PASS")
    except Exception as e:
        print_test("Lab Analyzer Agent", "FAIL", str(e))
    
    try:
        from agents.intelligent_image_analyzer import image_analyzer
        print_test("Image Analyzer Agent", "PASS")
    except Exception as e:
        print_test("Image Analyzer Agent", "FAIL", str(e))
    
    try:
        from agents.intelligent_risk_stratification import risk_stratifier
        print_test("Risk Stratifier Agent", "PASS")
    except Exception as e:
        print_test("Risk Stratifier Agent", "FAIL", str(e))
    
    try:
        from agents.healthcare_analytics import healthcare_analytics
        print_test("Healthcare Analytics Agent", "PASS")
    except Exception as e:
        print_test("Healthcare Analytics Agent", "FAIL", str(e))

def print_summary():
    """Print test summary"""
    print_header("Test Summary")
    
    total = len(test_results["passed"]) + len(test_results["failed"]) + len(test_results["warnings"])
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {len(test_results['passed'])}")
    print(f"❌ Failed: {len(test_results['failed'])}")
    print(f"⚠️  Warnings: {len(test_results['warnings'])}")
    
    if test_results["failed"]:
        print("\n❌ Failed Tests:")
        for test, message in test_results["failed"]:
            print(f"   - {test}: {message}")
    
    if test_results["warnings"]:
        print("\n⚠️  Warnings:")
        for test, message in test_results["warnings"]:
            print(f"   - {test}: {message}")
    
    # Overall status
    if not test_results["failed"]:
        print("\n✅ All critical tests passed! System is ready.")
    else:
        print("\n❌ Some tests failed. Please fix issues before deployment.")

async def main():
    """Run all tests"""
    print("\n🏥 Healthcare AI Multi-Agent System - Comprehensive Test Suite")
    print("Testing all components...\n")
    
    # Test server health
    if not await test_health_endpoint():
        print("\n❌ Server is not running! Start it with: python intelligent_orchestrator.py")
        return
    
    # Test static files
    await test_static_files()
    
    # Test WebSocket
    await test_websocket()
    
    # Test agent components
    await test_agent_components()
    
    # Test full pipeline
    analysis_results = await test_patient_analysis()
    
    # Test patient view
    await test_patient_view(analysis_results)
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    asyncio.run(main())
