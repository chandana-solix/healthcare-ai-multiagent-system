#!/usr/bin/env python3
"""
Test Runner for Healthcare AI Multi-Agent System
Tests different patient scenarios to verify proper UI behavior
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from intelligent_orchestrator import IntelligentOrchestrator
from agents.enhanced_patient_view import generate_ai_patient_view

class TestRunner:
    def __init__(self):
        self.orchestrator = IntelligentOrchestrator()
        self.test_dir = Path(__file__).parent / 'test_patients'
        self.results = []
        
    async def run_test_scenario(self, scenario_name: str, demographics_file: str, 
                              expected_results: dict) -> dict:
        """Run a single test scenario"""
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {scenario_name}")
        print(f"{'='*60}")
        
        # Use sample lab and xray images (you'll need to provide these)
        lab_path = str(self.test_dir.parent / 'sample_lab.jpg')
        xray_path = str(self.test_dir.parent / 'sample_xray.jpg')
        demo_path = str(self.test_dir / demographics_file)
        
        try:
            # Run analysis
            print("Running medical analysis...")
            analysis_results = await self.orchestrator.analyze_patient(
                demo_path, lab_path, xray_path
            )
            
            # Generate patient view
            print("Generating patient view...")
            patient_view = await generate_ai_patient_view(analysis_results)
            
            # Check results
            test_result = {
                'scenario': scenario_name,
                'passed': True,
                'checks': []
            }
            
            # Check risk level
            actual_risk = analysis_results['detailed_findings']['risk']['overall_risk']
            if 'risk' in expected_results:
                check_passed = actual_risk == expected_results['risk']
                test_result['checks'].append({
                    'name': 'Risk Level',
                    'expected': expected_results['risk'],
                    'actual': actual_risk,
                    'passed': check_passed
                })
                if not check_passed:
                    test_result['passed'] = False
            
            # Check alert display
            show_alert = patient_view['alert']['show_alert']
            if 'show_alert' in expected_results:
                check_passed = show_alert == expected_results['show_alert']
                test_result['checks'].append({
                    'name': 'Show Alert',
                    'expected': expected_results['show_alert'],
                    'actual': show_alert,
                    'passed': check_passed
                })
                if not check_passed:
                    test_result['passed'] = False
            
            # Check consensus score
            consensus_score = patient_view.get('medical_team_discussion', {}).get('consensus_score', 100)
            if 'low_consensus' in expected_results and expected_results['low_consensus']:
                check_passed = consensus_score < 60
                test_result['checks'].append({
                    'name': 'Low Consensus',
                    'expected': '<60%',
                    'actual': f'{consensus_score}%',
                    'passed': check_passed
                })
                if not check_passed:
                    test_result['passed'] = False
            
            # Check debate tab visibility
            show_debate = patient_view.get('show_debate_tab', False)
            if 'show_debate_tab' in expected_results:
                check_passed = show_debate == expected_results['show_debate_tab']
                test_result['checks'].append({
                    'name': 'Show Debate Tab',
                    'expected': expected_results['show_debate_tab'],
                    'actual': show_debate,
                    'passed': check_passed
                })
                if not check_passed:
                    test_result['passed'] = False
            
            # Print summary
            print(f"\n📊 Test Results for {scenario_name}:")
            print(f"   Overall: {'✅ PASSED' if test_result['passed'] else '❌ FAILED'}")
            for check in test_result['checks']:
                status = '✅' if check['passed'] else '❌'
                print(f"   {status} {check['name']}: Expected {check['expected']}, Got {check['actual']}")
            
            # Print key findings
            print(f"\n📋 Key Findings:")
            print(f"   Diagnosis: {analysis_results['consensus']['primary_diagnosis']}")
            print(f"   Disposition: {analysis_results['consensus']['disposition']}")
            print(f"   Alert Severity: {patient_view['alert'].get('severity', 'none')}")
            print(f"   Estimated Cost: ${patient_view['cost']['total_estimated']:,}")
            
            self.results.append(test_result)
            return test_result
            
        except Exception as e:
            print(f"❌ Error in test: {e}")
            import traceback
            traceback.print_exc()
            return {
                'scenario': scenario_name,
                'passed': False,
                'error': str(e)
            }
    
    async def run_all_tests(self):
        """Run all test scenarios"""
        print("\n🚀 Starting Healthcare AI Test Suite")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        test_scenarios = [
            {
                'name': 'Elderly with Low O2 but LOW Risk',
                'file': 'elderly_low_o2_low_risk.json',
                'expected': {
                    'risk': 'LOW',
                    'show_alert': False,
                    'show_debate_tab': False
                }
            },
            {
                'name': 'Young Adult with Pneumonia (HIGH Risk)',
                'file': 'young_pneumonia_high_risk.json',
                'expected': {
                    'risk': 'HIGH',
                    'show_alert': True,
                    'show_debate_tab': False
                }
            },
            {
                'name': 'Ambiguous Chest Pain (High Debate)',
                'file': 'ambiguous_chest_pain.json',
                'expected': {
                    'low_consensus': True,
                    'show_debate_tab': True
                }
            },
            {
                'name': 'Critical Sepsis',
                'file': 'critical_sepsis.json',
                'expected': {
                    'risk': 'CRITICAL',
                    'show_alert': True
                }
            }
        ]
        
        for scenario in test_scenarios:
            await self.run_test_scenario(
                scenario['name'],
                scenario['file'],
                scenario['expected']
            )
        
        # Print final summary
        print(f"\n{'='*60}")
        print("📊 FINAL TEST SUMMARY")
        print(f"{'='*60}")
        
        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed < total:
            print("\n❌ Some tests failed. Please review the results above.")
            return False
        else:
            print("\n✅ All tests passed! The system is working correctly.")
            return True

async def main():
    """Main test execution"""
    runner = TestRunner()
    success = await runner.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
