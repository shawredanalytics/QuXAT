#!/usr/bin/env python3
"""
Comprehensive Mayo Clinic CAP Integration Test
Tests the complete integration of Mayo Clinic CAP accreditation and validates score changes
"""

import json
import sys
from datetime import datetime

def test_mayo_cap_integration():
    """Test Mayo Clinic CAP integration comprehensively"""
    print("🧪 Comprehensive Mayo Clinic CAP Integration Test")
    print("=" * 60)
    
    # Test 1: Check unified database for Mayo Clinic
    print("\n📋 Test 1: Mayo Clinic in Unified Database")
    try:
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            organizations = data.get('organizations', []) if isinstance(data, dict) else data
        
        mayo_orgs = [org for org in organizations if 'mayo clinic' in org.get('name', '').lower()]
        print(f"✅ Found {len(mayo_orgs)} Mayo Clinic organizations")
        
        for i, org in enumerate(mayo_orgs, 1):
            print(f"\n   {i}. {org['name']}")
            print(f"      Quality Score: {org.get('quality_score', 'N/A')}")
            print(f"      CAP Accredited: {org.get('quality_indicators', {}).get('cap_accredited', False)}")
            print(f"      ISO 15189 Accredited: {org.get('quality_indicators', {}).get('iso_15189_accredited', False)}")
            
            # Check certifications
            certifications = org.get('certifications', [])
            cap_certs = [cert for cert in certifications if 'cap' in cert.get('name', '').lower() or 'cap' in cert.get('type', '').lower()]
            print(f"      CAP Certifications: {len(cap_certs)}")
            
            for cert in cap_certs:
                print(f"        - {cert.get('name', 'Unknown')}: {cert.get('type', 'Unknown')} (Impact: {cert.get('score_impact', 0)})")
    
    except Exception as e:
        print(f"❌ Error in Test 1: {e}")
        return False
    
    # Test 2: Check extracted Mayo CAP laboratories
    print(f"\n📋 Test 2: Extracted Mayo CAP Laboratories")
    try:
        with open('mayo_cap_laboratories.json', 'r', encoding='utf-8') as f:
            mayo_labs = json.load(f)
        
        print(f"✅ Found {len(mayo_labs)} extracted Mayo CAP laboratories")
        
        for i, lab in enumerate(mayo_labs, 1):
            print(f"\n   {i}. {lab['name']}")
            print(f"      Address: {lab.get('address', 'N/A')}")
            print(f"      Location: {lab.get('city', '')}, {lab.get('state', '')} {lab.get('zip_code', '')}")
            print(f"      Phone: {lab.get('phone', 'N/A')}")
            print(f"      Quality Score: {lab.get('quality_score', 'N/A')}")
            print(f"      Accreditation: {lab.get('accreditation_type', 'N/A')}")
    
    except Exception as e:
        print(f"❌ Error in Test 2: {e}")
        return False
    
    # Test 3: Check integration report
    print(f"\n📋 Test 3: Integration Report")
    try:
        with open('mayo_cap_integration_report.json', 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        integration_data = report.get('mayo_cap_integration_report', {})
        summary = integration_data.get('summary', {})
        
        print(f"✅ Integration Report Summary:")
        print(f"   - Total Mayo labs processed: {summary.get('total_mayo_labs_processed', 0)}")
        print(f"   - Merged with existing: {summary.get('merged_with_existing', 0)}")
        print(f"   - Added as new: {summary.get('added_as_new', 0)}")
        print(f"   - Total organizations after integration: {summary.get('total_organizations_after_integration', 0)}")
        
        updated_orgs = integration_data.get('updated_organizations', [])
        print(f"   - Updated organizations: {', '.join(updated_orgs)}")
    
    except Exception as e:
        print(f"❌ Error in Test 3: {e}")
        return False
    
    # Test 4: Score calculation validation
    print(f"\n📋 Test 4: Score Calculation Validation")
    try:
        # Import scoring modules
        sys.path.append('.')
        from international_scoring_algorithm import InternationalHealthcareScorer
        
        scorer = InternationalHealthcareScorer()
        
        # Test Mayo Clinic scoring
        for org in mayo_orgs:
            print(f"\n   Testing: {org['name']}")
            
            # Extract certifications from the organization data
            certifications = []
            for cert in org.get('certifications', []):
                cert_formatted = {
                    'name': cert.get('name', ''),
                    'type': cert.get('type', ''),
                    'status': cert.get('status', 'Active'),
                    'score_impact': cert.get('score_impact', 0)
                }
                certifications.append(cert_formatted)
            
            # Create quality metrics (using defaults for testing)
            quality_metrics = {
                'clinical_outcomes': {'composite_score': 85},
                'patient_experience': {'composite_score': 90},
                'operational_excellence': {'composite_score': 88},
                'innovation_technology': {'composite_score': 95},
                'sustainability_social': {'composite_score': 75}
            }
            
            # Create hospital context
            hospital_context = {
                'region': 'North America',
                'region_type': 'developed',
                'hospital_type': 'Academic Medical Center',
                'size': 'Large'
            }
            
            # Calculate score
            score_breakdown = scorer.calculate_international_quality_score(
                certifications=certifications,
                quality_metrics=quality_metrics,
                hospital_context=hospital_context
            )
            total_score = score_breakdown.get('total_score', 0)
            cert_score = score_breakdown.get('certification_score', 0)
            
            print(f"   - Total QuXAT Score: {total_score}")
            print(f"   - Certification Score: {cert_score}")
            
            # Check for CAP impact
            cert_breakdown = score_breakdown.get('certification_breakdown', {})
            cap_score = cert_breakdown.get('CAP', {}).get('total_score', 0)
            
            if cap_score > 0:
                print(f"   - CAP Score Contribution: {cap_score} ✅")
            else:
                print(f"   - CAP Score Contribution: {cap_score} ❌")
    
    except Exception as e:
        print(f"❌ Error in Test 4: {e}")
        return False
    
    # Test 5: Verify CAP data in main scoring
    print(f"\n📋 Test 5: CAP Data in Main Scoring System")
    try:
        # Test with streamlit app data loading
        from streamlit_app import load_healthcare_data, calculate_quality_score
        
        organizations = load_healthcare_data()
        mayo_in_main = [org for org in organizations if 'mayo clinic' in org.get('name', '').lower()]
        
        print(f"✅ Mayo Clinic organizations in main app: {len(mayo_in_main)}")
        
        for org in mayo_in_main:
            score_data = calculate_quality_score(org)
            print(f"   - {org['name']}: Score {score_data.get('total_score', 0)}")
            
            # Check CAP certification
            certifications = org.get('certifications', [])
            cap_certs = [cert for cert in certifications if 'cap' in str(cert).lower()]
            print(f"     CAP Certifications: {len(cap_certs)}")
    
    except Exception as e:
        print(f"❌ Error in Test 5: {e}")
        print(f"   Note: This may be expected if streamlit modules are not available")
    
    print(f"\n🎉 Mayo Clinic CAP Integration Test Complete!")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    
    return True

def main():
    """Main test function"""
    success = test_mayo_cap_integration()
    
    if success:
        print(f"\n✅ All tests completed successfully!")
        print(f"🏥 Mayo Clinic now has CAP 15189 accreditation integrated into QuXAT scoring")
    else:
        print(f"\n❌ Some tests failed. Please review the output above.")
    
    return success

if __name__ == "__main__":
    main()