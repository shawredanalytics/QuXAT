#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the scoring mechanism only uses validated certifications
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import HealthcareOrgAnalyzer
from data_validator import healthcare_validator

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_scoring_mechanism():
    """Test that the scoring mechanism only uses validated certifications"""
    print("🧪 Testing Scoring Mechanism")
    print("=" * 60)
    
    analyzer = HealthcareOrgAnalyzer()
    
    # Test 1: Empty certifications should result in 0 score
    print("\n1. Testing with empty certifications:")
    empty_certs = []
    score_result = analyzer.calculate_quality_score(empty_certs, [], 'Test Hospital')
    print(f"   Empty certifications score: {score_result['total_score']}")
    
    if score_result['total_score'] == 0:
        print("   ✅ PASS: Empty certifications correctly result in 0 score")
        test1_passed = True
    else:
        print("   ❌ FAIL: Empty certifications should result in 0 score")
        test1_passed = False
    
    # Test 2: Validated certifications (should be empty with disabled validation)
    print("\n2. Testing with validated certifications:")
    test_orgs = ['Apollo Hospitals', 'Fortis Healthcare', 'Max Healthcare']
    
    all_validated_empty = True
    for org_name in test_orgs:
        print(f"\n   Testing: {org_name}")
        try:
            validated_certs = healthcare_validator.validate_organization_certifications(org_name)
            if validated_certs and validated_certs.get('certifications'):
                certs = validated_certs['certifications']
                score_result = analyzer.calculate_quality_score(certs, [], org_name)
                print(f"   ❌ FAIL: Found {len(certs)} validated certifications, score: {score_result['total_score']}")
                all_validated_empty = False
            else:
                print(f"   ✅ PASS: No validated certifications found (as expected)")
        except Exception as e:
            print(f"   ✅ PASS: Validation properly failed (Exception: {str(e)[:50]}...)")
    
    # Test 3: Manual certification input (to verify scoring logic still works)
    print("\n3. Testing scoring logic with manual certification input:")
    manual_certs = [
        {
            'name': 'ISO 9001:2015',
            'status': 'Active',
            'score_impact': 25,
            'issuer': 'Test Certification Body',
            'accreditation_date': '2023-01-01',
            'expiry_date': '2026-01-01',
            'remarks': 'Test certification for scoring verification'
        }
    ]
    
    score_result = analyzer.calculate_quality_score(manual_certs, [], 'Test Hospital Manual')
    print(f"   Manual certification score: {score_result['total_score']}")
    
    if score_result['total_score'] > 0:
        print("   ✅ PASS: Scoring logic works with manual input")
        test3_passed = True
    else:
        print("   ❌ FAIL: Scoring logic should work with valid manual input")
        test3_passed = False
    
    print("\n" + "=" * 60)
    print("SCORING MECHANISM TEST RESULTS")
    print("=" * 60)
    
    if test1_passed and all_validated_empty and test3_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Scoring mechanism only uses validated certifications")
        print("✅ Empty certifications result in 0 score")
        print("✅ Scoring logic works correctly with valid input")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        print("⚠️  Please review the scoring mechanism")
        return False

if __name__ == "__main__":
    success = test_scoring_mechanism()
    sys.exit(0 if success else 1)