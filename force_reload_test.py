#!/usr/bin/env python3
"""
Force reload test for NABL scoring after database fix
This script bypasses any potential caching issues by directly loading the database
"""

import json
import sys
import os

def direct_database_test():
    """Test NABL scoring by directly loading the database"""
    print("🔄 Force Reload Test - Direct Database Loading")
    print("=" * 60)
    
    # Load database directly
    try:
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            database = json.load(f)
        print(f"✅ Loaded database with {len(database)} organizations")
    except Exception as e:
        print(f"❌ Error loading database: {e}")
        return False
    
    # Find Apex Hospitals Pvt. Ltd., Jaipur
    apex_org = None
    for org in database:
        if isinstance(org, dict):
            org_name = org.get('name', '')
            if 'Apex Hospitals Pvt. Ltd., Jaipur' in org_name:
                apex_org = org
                break
    
    if not apex_org:
        print("❌ Apex Hospitals Pvt. Ltd., Jaipur not found in database")
        return False
    
    print(f"✅ Found organization: {apex_org.get('name')}")
    
    # Check certifications directly from database
    certifications = apex_org.get('certifications', [])
    print(f"\n📋 Direct Database Check - Total Certifications: {len(certifications)}")
    
    nabl_certs = []
    for i, cert in enumerate(certifications, 1):
        cert_name = cert.get('name', 'N/A')
        cert_type = cert.get('type', 'N/A')
        status = cert.get('status', 'N/A')
        score_impact = cert.get('score_impact', 0)
        cert_number = cert.get('certificate_number', 'N/A')
        
        print(f"   Cert {i}:")
        print(f"     Name: {cert_name}")
        print(f"     Type: {cert_type}")
        print(f"     Status: {status}")
        print(f"     Score Impact: {score_impact}")
        if cert_number != 'N/A':
            print(f"     Certificate Number: {cert_number}")
        
        # Check if this is a NABL certificate
        if 'NABL' in cert_name.upper() or 'NABL' in cert_type.upper():
            nabl_certs.append(cert)
    
    print(f"\n🎯 NABL Certifications found in database: {len(nabl_certs)}")
    
    active_nabl_score = 0
    mc6208_found = False
    
    for i, cert in enumerate(nabl_certs, 1):
        cert_name = cert.get('name', 'N/A')
        cert_type = cert.get('type', 'N/A')
        status = cert.get('status', 'N/A')
        score_impact = cert.get('score_impact', 0)
        cert_number = cert.get('certificate_number', 'N/A')
        expiry_date = cert.get('expiry_date', 'N/A')
        
        print(f"   NABL Cert {i}:")
        print(f"     Name: {cert_name}")
        print(f"     Type: {cert_type}")
        print(f"     Status: {status}")
        print(f"     Score Impact: {score_impact}")
        print(f"     Certificate Number: {cert_number}")
        print(f"     Expiry Date: {expiry_date}")
        
        if cert_number == 'MC-6208':
            mc6208_found = True
            print(f"     ✅ MC-6208 certificate found!")
        
        if status == 'Active':
            active_nabl_score += score_impact
            print(f"     ✅ Active certificate - adding {score_impact} points")
        else:
            print(f"     ❌ Not active - status: {status}")
    
    print(f"\n📊 Database Analysis Results:")
    print(f"   • MC-6208 Certificate Found: {'✅ YES' if mc6208_found else '❌ NO'}")
    print(f"   • Total Active NABL Score: {active_nabl_score}")
    print(f"   • Expected NABL Points: 15.0 (if MC-6208 is active)")
    
    # Check quality indicators in database
    quality_indicators = apex_org.get('quality_indicators', {})
    db_nabl_accredited = quality_indicators.get('nabl_accredited', False)
    db_nabl_score = quality_indicators.get('nabl_score', 0)
    
    print(f"\n🔍 Database Quality Indicators:")
    print(f"   • NABL Accredited: {db_nabl_accredited}")
    print(f"   • NABL Score: {db_nabl_score}")
    
    # Now test with the analyzer
    print(f"\n🧪 Testing with HealthcareOrgAnalyzer...")
    
    try:
        # Import and initialize analyzer
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from streamlit_app import HealthcareOrgAnalyzer
        
        # Create new instance to force reload
        analyzer = HealthcareOrgAnalyzer()
        
        # Search for the organization
        org_info = analyzer.search_organization_info("Apex Hospitals Pvt. Ltd., Jaipur")
        
        if not org_info:
            print("❌ Organization not found via analyzer")
            return False
        
        print(f"✅ Found via analyzer: {org_info.get('name')}")
        
        # Check certifications from analyzer
        analyzer_certs = org_info.get('certifications', [])
        analyzer_nabl_certs = [cert for cert in analyzer_certs if 'NABL' in cert.get('name', '').upper() or 'NABL' in cert.get('type', '').upper()]
        
        print(f"📋 Analyzer Results:")
        print(f"   • Total Certifications: {len(analyzer_certs)}")
        print(f"   • NABL Certifications: {len(analyzer_nabl_certs)}")
        
        for cert in analyzer_nabl_certs:
            print(f"     - {cert.get('certificate_number', 'N/A')}: {cert.get('status', 'N/A')} (Score: {cert.get('score_impact', 0)})")
        
        # Test scoring with proper parameters
        print(f"\n🎯 Testing scoring...")
        
        try:
            # Get quality initiatives (empty list if none)
            initiatives = org_info.get('quality_initiatives', [])
            
            # Calculate score with proper parameters
            score_result = analyzer.calculate_quality_score(org_info, initiatives)
            
            print(f"📊 Scoring Results:")
            print(f"   • Total Score: {score_result.get('total_score', 0)}")
            print(f"   • Certification Score: {score_result.get('certification_score', 0)}")
            
            # Check score breakdown
            score_breakdown = score_result.get('score_breakdown', {})
            nabl_score_in_breakdown = score_breakdown.get('NABL Accreditation Score', 'NOT FOUND')
            print(f"   • NABL Score in Breakdown: {nabl_score_in_breakdown}")
            
            # Check quality indicators from scoring
            quality_indicators = score_result.get('quality_indicators', {})
            scoring_nabl_accredited = quality_indicators.get('nabl_accredited', False)
            scoring_nabl_score = quality_indicators.get('nabl_score', 0)
            
            print(f"   • Scoring NABL Accredited: {scoring_nabl_accredited}")
            print(f"   • Scoring NABL Score: {scoring_nabl_score}")
            
            # Final assessment
            print(f"\n🎯 Final Assessment:")
            if mc6208_found and scoring_nabl_score > 0 and scoring_nabl_accredited:
                print("   ✅ SUCCESS: NABL certificate fix is working!")
                print("   ✅ MC-6208 certificate is being properly loaded and scored")
                return True
            else:
                print("   ❌ ISSUE: Problems detected")
                if not mc6208_found:
                    print("   ❌ MC-6208 certificate not found in database")
                if scoring_nabl_score == 0:
                    print("   ❌ NABL score is still 0 in scoring results")
                if not scoring_nabl_accredited:
                    print("   ❌ Organization not marked as NABL accredited in scoring")
                return False
                
        except Exception as e:
            print(f"❌ Error during scoring: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error with analyzer: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = direct_database_test()
    if success:
        print("\n🎉 Force reload test PASSED!")
        print("   The NABL certificate fix is working correctly.")
    else:
        print("\n❌ Force reload test FAILED!")
        print("   Additional investigation needed.")
        sys.exit(1)