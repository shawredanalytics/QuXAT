#!/usr/bin/env python3
"""
Test script for the new mandatory ISO scoring system
This script demonstrates how the QuXAT scoring system now handles mandatory ISO standards
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import HealthcareOrgAnalyzer

def test_mandatory_iso_system():
    """Test the mandatory ISO scoring system with different compliance scenarios"""
    
    print("🧪 TESTING MANDATORY ISO SCORING SYSTEM")
    print("=" * 60)
    
    analyzer = HealthcareOrgAnalyzer()
    
    # Test Case 1: Organization with ALL mandatory ISO standards (Full Compliance)
    print("\n📋 TEST CASE 1: FULL COMPLIANCE - All Mandatory ISO Standards Present")
    print("-" * 60)
    
    compliant_certifications = [
        {'name': 'ISO 9001:2015 Quality Management', 'status': 'Active', 'issuer': 'BSI'},
        {'name': 'ISO 13485:2016 Medical Devices', 'status': 'Active', 'issuer': 'TUV'},
        {'name': 'ISO 15189:2012 Medical Laboratories', 'status': 'Active', 'issuer': 'ANAB'},
        {'name': 'ISO 27001:2013 Information Security', 'status': 'Active', 'issuer': 'BSI'},
        {'name': 'ISO 45001:2018 Occupational Health', 'status': 'Active', 'issuer': 'SGS'},
        {'name': 'ISO 14001:2015 Environmental Management', 'status': 'Active', 'issuer': 'DNV'},
        {'name': 'CAP Laboratory Accreditation', 'status': 'Active', 'issuer': 'CAP'},
        {'name': 'JCI Hospital Accreditation', 'status': 'Active', 'issuer': 'JCI'}
    ]
    
    compliant_initiatives = [
        {'name': 'Patient Safety Program', 'status': 'Active'},
        {'name': 'Quality Improvement Initiative', 'status': 'Active'}
    ]
    
    score_breakdown = analyzer.calculate_quality_score(
        compliant_certifications, 
        compliant_initiatives, 
        "Excellence Medical Center"
    )
    
    print(f"Organization: Excellence Medical Center")
    print(f"Total Certifications: {len(compliant_certifications)}")
    print(f"Certification Score: {score_breakdown['certification_score']:.2f}/75")
    print(f"Quality Initiatives Score: {score_breakdown['quality_initiatives_score']:.2f}/35")
    print(f"Mandatory Penalty: -{score_breakdown.get('mandatory_penalty', 0):.2f} points")
    print(f"Final Score: {score_breakdown['total_score']:.2f}/110")
    
    compliance_check = score_breakdown.get('compliance_check', {})
    print(f"Compliance Status: {'✅ COMPLIANT' if compliance_check.get('is_fully_compliant', False) else '❌ NON-COMPLIANT'}")
    
    # Test Case 2: Organization with MISSING mandatory ISO standards (Non-Compliance)
    print("\n📋 TEST CASE 2: NON-COMPLIANCE - Missing Mandatory ISO Standards")
    print("-" * 60)
    
    non_compliant_certifications = [
        {'name': 'NABH Hospital Accreditation', 'status': 'Active', 'issuer': 'NABH'},
        {'name': 'ISO 50001:2018 Energy Management', 'status': 'Active', 'issuer': 'BSI'},
        # Missing: ISO 9001, ISO 13485, ISO 15189, ISO 27001, ISO 45001, ISO 14001, CAP
    ]
    
    non_compliant_initiatives = [
        {'name': 'Basic Quality Program', 'status': 'Active'}
    ]
    
    score_breakdown = analyzer.calculate_quality_score(
        non_compliant_certifications, 
        non_compliant_initiatives, 
        "Basic Healthcare Facility"
    )
    
    print(f"Organization: Basic Healthcare Facility")
    print(f"Total Certifications: {len(non_compliant_certifications)}")
    print(f"Certification Score: {score_breakdown['certification_score']:.2f}/75")
    print(f"Quality Initiatives Score: {score_breakdown['quality_initiatives_score']:.2f}/35")
    print(f"Mandatory Penalty: -{score_breakdown.get('mandatory_penalty', 0):.2f} points")
    print(f"Final Score: {score_breakdown['total_score']:.2f}/110")
    
    compliance_check = score_breakdown.get('compliance_check', {})
    print(f"Compliance Status: {'✅ COMPLIANT' if compliance_check.get('is_fully_compliant', False) else '❌ NON-COMPLIANT'}")
    print(f"Missing Standards: {compliance_check.get('missing_critical_standards', [])}")
    
    # Test Case 3: Organization with PARTIAL compliance (Some mandatory standards)
    print("\n📋 TEST CASE 3: PARTIAL COMPLIANCE - Some Mandatory ISO Standards")
    print("-" * 60)
    
    partial_certifications = [
        {'name': 'ISO 9001:2015 Quality Management', 'status': 'Active', 'issuer': 'BSI'},
        {'name': 'ISO 27001:2013 Information Security', 'status': 'Active', 'issuer': 'BSI'},
        {'name': 'CAP Laboratory Accreditation', 'status': 'Active', 'issuer': 'CAP'},
        {'name': 'NABH Hospital Accreditation', 'status': 'Active', 'issuer': 'NABH'},
        # Missing: ISO 13485, ISO 15189, ISO 45001, ISO 14001
    ]
    
    partial_initiatives = [
        {'name': 'Quality Improvement Program', 'status': 'Active'},
        {'name': 'Patient Safety Initiative', 'status': 'Active'}
    ]
    
    score_breakdown = analyzer.calculate_quality_score(
        partial_certifications, 
        partial_initiatives, 
        "Developing Medical Center"
    )
    
    print(f"Organization: Developing Medical Center")
    print(f"Total Certifications: {len(partial_certifications)}")
    print(f"Certification Score: {score_breakdown['certification_score']:.2f}/75")
    print(f"Quality Initiatives Score: {score_breakdown['quality_initiatives_score']:.2f}/35")
    print(f"Mandatory Penalty: -{score_breakdown.get('mandatory_penalty', 0):.2f} points")
    print(f"Final Score: {score_breakdown['total_score']:.2f}/110")
    
    compliance_check = score_breakdown.get('compliance_check', {})
    print(f"Compliance Status: {'✅ COMPLIANT' if compliance_check.get('is_fully_compliant', False) else '❌ NON-COMPLIANT'}")
    print(f"Missing Standards: {compliance_check.get('missing_critical_standards', [])}")
    
    # Summary Analysis
    print("\n📊 MANDATORY ISO SYSTEM ANALYSIS")
    print("=" * 60)
    print("✅ BENEFITS OF THE NEW SYSTEM:")
    print("   • Clear penalties for missing mandatory standards")
    print("   • Balanced scoring with room for improvement")
    print("   • Transparent compliance tracking")
    print("   • Incentivizes international quality standards")
    print("   • Maintains competitive scoring for compliant organizations")
    
    print("\n🎯 SCORING METHODOLOGY:")
    print("   • Maximum Score: 110 points (75 certifications + 35 quality initiatives)")
    print("   • Mandatory ISO Penalties: Up to 69 points total")
    print("   • Balanced approach ensures improvement opportunities")
    print("   • Clear compliance status messaging")

if __name__ == "__main__":
    test_mandatory_iso_system()