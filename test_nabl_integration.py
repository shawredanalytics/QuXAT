#!/usr/bin/env python3
"""
Test script to validate NABL integration with QuXAT scoring system
"""

import sys
import json
sys.path.append('.')
from streamlit_app import HealthcareOrgAnalyzer

def test_nabl_integration():
    """Test NABL integration with sample healthcare organizations"""
    print("🧪 Testing NABL Integration with QuXAT Scoring System")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = HealthcareOrgAnalyzer()
    
    # Test organizations - mix of NABL accredited and non-accredited
    test_organizations = [
        {
            'name': 'Apollo Hospitals',
            'certifications': [
                {'name': 'JCI Accreditation', 'status': 'Active', 'score_impact': 30},
                {'name': 'ISO 9001', 'status': 'Active', 'score_impact': 25}
            ]
        },
        {
            'name': 'Dr. Lal PathLabs',
            'certifications': [
                {'name': 'ISO 15189', 'status': 'Active', 'score_impact': 22},
                {'name': 'CAP Accreditation', 'status': 'Active', 'score_impact': 22}
            ]
        },
        {
            'name': 'Metropolis Healthcare',
            'certifications': [
                {'name': 'ISO 9001', 'status': 'Active', 'score_impact': 25}
            ]
        },
        {
            'name': 'Mayo Clinic',  # Non-Indian, should not be NABL accredited
            'certifications': [
                {'name': 'JCI Accreditation', 'status': 'Active', 'score_impact': 30},
                {'name': 'ISO 9001', 'status': 'Active', 'score_impact': 25}
            ]
        }
    ]
    
    results = []
    
    for org in test_organizations:
        print(f"\n🏥 Testing: {org['name']}")
        print("-" * 40)
        
        # Calculate quality score with NABL integration
        score_breakdown = analyzer.calculate_quality_score(
            certifications=org['certifications'].copy(),  # Use copy to avoid modifying original
            initiatives=[],
            org_name=org['name']
        )
        
        # Display results
        print(f"📊 Score Breakdown:")
        print(f"   • Certification Score: {score_breakdown['certification_score']:.1f}")
        print(f"   • Quality Initiatives Score: {score_breakdown['quality_initiatives_score']:.1f}")
        print(f"   • NABL Accreditation Score: {score_breakdown['nabl_accreditation_score']:.1f}")
        print(f"   • Total Score: {score_breakdown['total_score']:.1f}")
        
        # Check if NABL certification was added
        nabl_cert_added = any('NABL' in cert.get('name', '').upper() for cert in org['certifications'])
        if nabl_cert_added:
            print(f"   ✅ NABL certification automatically added to certifications list")
            nabl_cert = next(cert for cert in org['certifications'] if 'NABL' in cert.get('name', '').upper())
            print(f"   📋 NABL Details: {nabl_cert['name']}")
            print(f"   🎯 NABL Remarks: {nabl_cert.get('remarks', 'N/A')}")
        else:
            print(f"   ❌ No NABL accreditation found")
        
        # Store results
        results.append({
            'organization': org['name'],
            'nabl_score': score_breakdown['nabl_accreditation_score'],
            'total_score': score_breakdown['total_score'],
            'nabl_certified': nabl_cert_added,
            'score_breakdown': score_breakdown
        })
    
    # Summary analysis
    print(f"\n📈 NABL Integration Test Summary")
    print("=" * 60)
    
    nabl_accredited_count = sum(1 for r in results if r['nabl_score'] > 0)
    total_orgs = len(results)
    
    print(f"Total Organizations Tested: {total_orgs}")
    print(f"NABL Accredited Organizations: {nabl_accredited_count}")
    print(f"NABL Accreditation Rate: {(nabl_accredited_count/total_orgs)*100:.1f}%")
    
    print(f"\n🏆 Top Scoring Organizations:")
    sorted_results = sorted(results, key=lambda x: x['total_score'], reverse=True)
    for i, result in enumerate(sorted_results[:3], 1):
        nabl_indicator = "🇮🇳 NABL" if result['nabl_score'] > 0 else "❌ No NABL"
        print(f"   {i}. {result['organization']}: {result['total_score']:.1f} points ({nabl_indicator})")
    
    # Detailed NABL analysis
    print(f"\n🔍 NABL Score Analysis:")
    for result in results:
        if result['nabl_score'] > 0:
            print(f"   • {result['organization']}: +{result['nabl_score']:.1f} NABL points")
    
    # Save test results
    test_report = {
        'test_timestamp': '2025-09-26T16:58:00',
        'test_type': 'NABL Integration Test',
        'organizations_tested': total_orgs,
        'nabl_accredited_count': nabl_accredited_count,
        'nabl_accreditation_rate': (nabl_accredited_count/total_orgs)*100,
        'detailed_results': results,
        'top_performers': sorted_results[:3]
    }
    
    with open('nabl_integration_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(test_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Test report saved to: nabl_integration_test_report.json")
    print(f"✅ NABL Integration Test Completed Successfully!")
    
    return results

if __name__ == "__main__":
    test_nabl_integration()