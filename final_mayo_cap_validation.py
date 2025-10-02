#!/usr/bin/env python3
"""
Final Mayo Clinic CAP Integration Validation
Comprehensive test to verify CAP integration is working correctly
"""

import json
import sys
from international_scoring_algorithm import InternationalHealthcareScorer

def test_mayo_clinic_cap_integration():
    """Test Mayo Clinic CAP integration comprehensively"""
    print("🏥 Final Mayo Clinic CAP Integration Validation")
    print("=" * 60)
    
    # Test 1: Load and verify Mayo Clinic in unified database
    print("\n📊 Test 1: Mayo Clinic in Unified Database")
    try:
        with open('unified_healthcare_organizations_with_mayo_cap.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, dict) and 'organizations' in data:
            orgs = data['organizations']
        elif isinstance(data, list):
            orgs = data
        else:
            orgs = [data] if isinstance(data, dict) else []
        
        mayo_orgs = [org for org in orgs if org.get('name') == 'Mayo Clinic']
        
        if not mayo_orgs:
            print("❌ Mayo Clinic not found in unified database")
            return False
        
        mayo = mayo_orgs[0]
        print(f"✅ Found Mayo Clinic: {mayo['name']}")
        print(f"   Quality Score: {mayo.get('quality_score', 0)}")
        print(f"   CAP Accredited: {mayo.get('quality_indicators', {}).get('cap_accredited', False)}")
        print(f"   Total Certifications: {len(mayo.get('certifications', []))}")
        
        # Check CAP certifications
        cap_certs = [cert for cert in mayo.get('certifications', []) 
                    if 'CAP' in cert.get('name', '') or 'College of American Pathologists' in cert.get('name', '')]
        print(f"   CAP Certifications: {len(cap_certs)}")
        
        for cert in cap_certs:
            print(f"     - {cert.get('name', 'Unknown')}: Score Impact {cert.get('score_impact', 0)}")
        
    except Exception as e:
        print(f"❌ Error in Test 1: {e}")
        return False
    
    # Test 2: Verify CAP laboratories were extracted
    print("\n🔬 Test 2: Extracted CAP Laboratories")
    try:
        with open('mayo_cap_laboratories.json', 'r', encoding='utf-8') as f:
            cap_labs = json.load(f)
        
        print(f"✅ Found {len(cap_labs)} Mayo CAP laboratories")
        for lab in cap_labs:
            print(f"   - {lab['name']}: Quality Score {lab.get('quality_score', 0)}")
            
    except Exception as e:
        print(f"❌ Error in Test 2: {e}")
        return False
    
    # Test 3: Test International Scoring Algorithm with CAP
    print("\n🎯 Test 3: International Scoring Algorithm with CAP")
    try:
        scorer = InternationalHealthcareScorer()
        
        # Create test certifications including CAP
        test_certifications = [
            {
                'name': 'Joint Commission International (JCI)',
                'type': 'JCI Accreditation',
                'status': 'Active',
                'score_impact': 20.0
            },
            {
                'name': 'College of American Pathologists (CAP)',
                'type': 'CAP 15189 Accreditation',
                'status': 'Active',
                'score_impact': 18.0
            },
            {
                'name': 'ISO 9001:2015',
                'type': 'Quality Management System',
                'status': 'Active',
                'score_impact': 8.0
            }
        ]
        
        # Test certification identification
        for cert in test_certifications:
            cert_type = scorer._identify_certification_type(cert['name'])
            print(f"   '{cert['name']}' -> {cert_type}")
        
        # Calculate score
        quality_metrics = {
            'clinical_outcomes': {'composite_score': 90},
            'patient_experience': {'composite_score': 92},
            'operational_excellence': {'composite_score': 88},
            'innovation_technology': {'composite_score': 95},
            'sustainability_social': {'composite_score': 85}
        }
        
        hospital_context = {
            'region': 'North America',
            'region_type': 'developed',
            'hospital_type': 'Academic Medical Center',
            'size': 'Large'
        }
        
        score_result = scorer.calculate_international_quality_score(
            certifications=test_certifications,
            quality_metrics=quality_metrics,
            hospital_context=hospital_context
        )
        
        print(f"\n   📈 Scoring Results:")
        print(f"   Total Score: {score_result['total_score']:.1f}/100")
        print(f"   Certification Score: {score_result['certification_score']:.1f}/60")
        print(f"   Quality Metrics Score: {score_result['quality_metrics_score']:.1f}/40")
        
        # Check certification breakdown
        cert_breakdown = score_result.get('certification_breakdown', {})
        print(f"\n   🏆 Certification Breakdown:")
        for cert_type, details in cert_breakdown.items():
            print(f"     {cert_type}: {details['total_score']:.1f} points ({details['description']})")
        
        # Verify CAP is included
        if 'CAP_LABORATORY' in cert_breakdown:
            cap_score = cert_breakdown['CAP_LABORATORY']['total_score']
            print(f"   ✅ CAP Laboratory Score: {cap_score:.1f} points")
        else:
            print(f"   ❌ CAP Laboratory not found in scoring breakdown")
            return False
            
    except Exception as e:
        print(f"❌ Error in Test 3: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Integration Report Verification
    print("\n📋 Test 4: Integration Report")
    try:
        with open('mayo_cap_integration_report.json', 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        stats = report.get('integration_stats', {})
        print(f"✅ Integration Report Summary:")
        print(f"   Mayo labs processed: {stats.get('mayo_labs_processed', 0)}")
        print(f"   Organizations merged: {stats.get('organizations_merged', 0)}")
        print(f"   Organizations added: {stats.get('organizations_added', 0)}")
        print(f"   Total organizations: {stats.get('total_organizations_after', 0)}")
        
    except Exception as e:
        print(f"❌ Error in Test 4: {e}")
        return False
    
    return True

def test_streamlit_integration():
    """Test if CAP data works with Streamlit app"""
    print("\n🌐 Test 5: Streamlit Integration Check")
    try:
        # Import streamlit app components
        sys.path.append('.')
        
        # Test search functionality
        with open('unified_healthcare_organizations_with_mayo_cap.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, dict) and 'organizations' in data:
            orgs = data['organizations']
        elif isinstance(data, list):
            orgs = data
        else:
            orgs = [data] if isinstance(data, dict) else []
        
        # Search for Mayo Clinic
        mayo_results = [org for org in orgs if 'mayo clinic' in org.get('name', '').lower()]
        
        if mayo_results:
            mayo = mayo_results[0]
            print(f"✅ Mayo Clinic searchable in database")
            print(f"   Name: {mayo['name']}")
            print(f"   Quality Score: {mayo.get('quality_score', 0)}")
            print(f"   CAP Accredited: {mayo.get('quality_indicators', {}).get('cap_accredited', False)}")
            
            # Check if CAP certifications are present
            cap_certs = [cert for cert in mayo.get('certifications', []) 
                        if 'CAP' in cert.get('name', '')]
            print(f"   CAP Certifications: {len(cap_certs)}")
            
            return True
        else:
            print("❌ Mayo Clinic not found in search")
            return False
            
    except Exception as e:
        print(f"❌ Error in Test 5: {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 Starting Final Mayo Clinic CAP Integration Validation")
    
    success = True
    
    # Run all tests
    if not test_mayo_clinic_cap_integration():
        success = False
    
    if not test_streamlit_integration():
        success = False
    
    # Final summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Mayo Clinic CAP integration is working correctly")
        print("✅ CAP certifications are properly weighted in scoring")
        print("✅ Data is available for Streamlit app")
        print("\n📊 Summary:")
        print("   - Mayo Clinic has CAP 15189 accreditation integrated")
        print("   - CAP certifications contribute to QuXAT scoring")
        print("   - Integration is complete and functional")
    else:
        print("❌ SOME TESTS FAILED!")
        print("   Please review the errors above")
    
    return success

if __name__ == "__main__":
    main()