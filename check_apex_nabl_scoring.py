#!/usr/bin/env python3
"""
Check Apex Hospitals Jaipur NABL Accreditation and Scoring Status
"""

import json
import sys
from datetime import datetime

def check_apex_nabl_status():
    """Check Apex Hospitals Jaipur NABL status and scoring"""
    
    print("=" * 80)
    print("APEX HOSPITALS JAIPUR - NABL ACCREDITATION & SCORING CHECK")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Load the unified healthcare organizations database
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            organizations = json.load(f)
        
        print(f"✅ Loaded {len(organizations)} organizations from database")
        print()
        
        # Search for Apex Hospitals entries
        apex_entries = []
        for org in organizations:
            org_name = org.get('name', '').lower()
            if 'apex' in org_name and 'hospital' in org_name:
                apex_entries.append(org)
        
        print(f"🔍 Found {len(apex_entries)} Apex Hospital entries:")
        print("-" * 60)
        
        for i, org in enumerate(apex_entries, 1):
            print(f"\n{i}. Organization: {org.get('name', 'N/A')}")
            print(f"   Location: {org.get('location', 'N/A')}")
            print(f"   Data Source: {org.get('data_source', 'N/A')}")
            print(f"   NABL Accredited: {org.get('nabl_accredited', False)}")
            
            # Check certifications
            certifications = org.get('certifications', [])
            nabl_certs = [cert for cert in certifications if cert.get('type') == 'NABL Accreditation']
            
            print(f"   Total Certifications: {len(certifications)}")
            print(f"   NABL Certifications: {len(nabl_certs)}")
            
            if nabl_certs:
                for j, cert in enumerate(nabl_certs, 1):
                    print(f"     NABL Cert {j}:")
                    print(f"       Certificate Number: {cert.get('certificate_number', 'N/A')}")
                    print(f"       Status: {cert.get('status', 'N/A')}")
                    print(f"       Issue Date: {cert.get('issue_date', 'N/A')}")
                    print(f"       Expiry Date: {cert.get('expiry_date', 'N/A')}")
                    print(f"       Score Impact: {cert.get('score_impact', 0)}")
                    print(f"       Data Source: {cert.get('data_source', 'N/A')}")
            
            # Check quality indicators
            quality_indicators = org.get('quality_indicators', {})
            print(f"   Quality Indicators:")
            print(f"     NABL Score: {quality_indicators.get('nabl_score', 0)}")
            print(f"     Total Score: {quality_indicators.get('total_score', 0)}")
            
            # Check QuXAT score
            quxat_score = org.get('quxat_score', 0)
            print(f"   QuXAT Score: {quxat_score}")
            
        # Check overall NABL statistics
        print("\n" + "=" * 60)
        print("OVERALL NABL STATISTICS")
        print("=" * 60)
        
        total_nabl_orgs = 0
        active_nabl_certs = 0
        total_nabl_score = 0
        
        for org in organizations:
            if org.get('nabl_accredited', False):
                total_nabl_orgs += 1
                
                certifications = org.get('certifications', [])
                for cert in certifications:
                    if cert.get('type') == 'NABL Accreditation' and cert.get('status') == 'Active':
                        active_nabl_certs += 1
                        total_nabl_score += cert.get('score_impact', 0)
        
        print(f"Total NABL Accredited Organizations: {total_nabl_orgs}")
        print(f"Active NABL Certificates: {active_nabl_certs}")
        print(f"Total NABL Score Impact: {total_nabl_score}")
        
        # Specific check for Apex Hospitals Pvt. Ltd., Jaipur
        print("\n" + "=" * 60)
        print("SPECIFIC CHECK: APEX HOSPITALS PVT. LTD., JAIPUR")
        print("=" * 60)
        
        apex_jaipur = None
        for org in organizations:
            org_name = org.get('name', '')
            location = org.get('location', '')
            if ('Apex Hospitals Pvt. Ltd.' in org_name and 
                ('Jaipur' in location or 'Rajasthan' in location)):
                apex_jaipur = org
                break
        
        if apex_jaipur:
            print(f"✅ Found: {apex_jaipur.get('name', 'N/A')}")
            print(f"Location: {apex_jaipur.get('location', 'N/A')}")
            print(f"NABL Accredited: {apex_jaipur.get('nabl_accredited', False)}")
            
            # Check NABL certifications
            certifications = apex_jaipur.get('certifications', [])
            nabl_certs = [cert for cert in certifications if cert.get('type') == 'NABL Accreditation']
            
            print(f"NABL Certificates: {len(nabl_certs)}")
            
            nabl_score_total = 0
            for cert in nabl_certs:
                score_impact = cert.get('score_impact', 0)
                nabl_score_total += score_impact
                print(f"  - Certificate: {cert.get('certificate_number', 'N/A')}")
                print(f"    Status: {cert.get('status', 'N/A')}")
                print(f"    Score Impact: {score_impact}")
            
            # Check quality indicators
            quality_indicators = apex_jaipur.get('quality_indicators', {})
            nabl_score = quality_indicators.get('nabl_score', 0)
            total_score = quality_indicators.get('total_score', 0)
            
            print(f"Quality Indicators NABL Score: {nabl_score}")
            print(f"Quality Indicators Total Score: {total_score}")
            print(f"QuXAT Score: {apex_jaipur.get('quxat_score', 0)}")
            
            # Verify scoring calculation
            print(f"\nScoring Verification:")
            print(f"  Certificate Score Total: {nabl_score_total}")
            print(f"  Quality Indicators NABL: {nabl_score}")
            print(f"  Match: {'✅ YES' if nabl_score_total == nabl_score else '❌ NO - MISMATCH!'}")
            
            if nabl_score_total != nabl_score:
                print(f"  ⚠️  SCORING ISSUE DETECTED!")
                print(f"     Expected NABL Score: {nabl_score_total}")
                print(f"     Actual NABL Score: {nabl_score}")
        else:
            print("❌ Apex Hospitals Pvt. Ltd., Jaipur NOT FOUND!")
        
        print("\n" + "=" * 80)
        print("CHECK COMPLETED")
        print("=" * 80)
        
    except FileNotFoundError:
        print("❌ Error: unified_healthcare_organizations.json not found!")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format - {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = check_apex_nabl_status()
    sys.exit(0 if success else 1)