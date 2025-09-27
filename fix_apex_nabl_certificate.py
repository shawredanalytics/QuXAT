#!/usr/bin/env python3
"""
Fix Apex Hospitals NABL Certificate Assignment
Corrects the MC-6208 certificate to be properly assigned to Apex Hospitals Pvt. Ltd.
"""

import json
from datetime import datetime

def fix_apex_nabl_certificate():
    """Fix the NABL certificate assignment for Apex Hospitals"""
    
    print("=== Fixing Apex Hospitals NABL Certificate Assignment ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load unified database
    try:
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            organizations = json.load(f)
        
        print(f"Total organizations loaded: {len(organizations)}")
        
    except Exception as e:
        print(f"Error loading database: {e}")
        return
    
    # Create backup
    backup_filename = f"unified_healthcare_organizations_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(organizations, f, indent=2, ensure_ascii=False)
        print(f"Backup created: {backup_filename}")
    except Exception as e:
        print(f"Error creating backup: {e}")
        return
    
    # Find organizations with MC-6208 certificate
    mc6208_orgs = []
    apex_hospitals_org = None
    
    for i, org in enumerate(organizations):
        if not isinstance(org, dict):
            continue
        
        org_name = org.get('name', '')
        
        # Find Apex Hospitals
        if 'Apex Hospitals Pvt. Ltd.' in org_name:
            apex_hospitals_org = (i, org)
            print(f"Found Apex Hospitals: {org_name}")
        
        # Find organizations with MC-6208 certificate
        certifications = org.get('certifications', [])
        for cert in certifications:
            if isinstance(cert, dict) and cert.get('certificate_number') == 'MC-6208':
                mc6208_orgs.append((i, org, cert))
                print(f"Found MC-6208 certificate in: {org_name}")
    
    print()
    
    if not apex_hospitals_org:
        print("Error: Apex Hospitals Pvt. Ltd. not found in database")
        return
    
    if not mc6208_orgs:
        print("Error: MC-6208 certificate not found in database")
        return
    
    # Remove MC-6208 from incorrect organizations
    for org_idx, org, cert in mc6208_orgs:
        org_name = org.get('name', '')
        if 'Apex Hospitals' not in org_name:
            print(f"Removing MC-6208 from incorrect organization: {org_name}")
            
            # Remove the NABL certificate
            certifications = org.get('certifications', [])
            updated_certs = [c for c in certifications if not (isinstance(c, dict) and c.get('certificate_number') == 'MC-6208')]
            organizations[org_idx]['certifications'] = updated_certs
            
            # Update data source
            data_source = org.get('data_source', '')
            if '+NABL' in data_source:
                organizations[org_idx]['data_source'] = data_source.replace('+NABL', '')
            elif data_source == 'NABL':
                organizations[org_idx]['data_source'] = 'Unknown'
            
            # Update quality indicators
            quality_indicators = org.get('quality_indicators', {})
            if isinstance(quality_indicators, dict):
                quality_indicators['nabl_accredited'] = False
                organizations[org_idx]['quality_indicators'] = quality_indicators
    
    # Add correct MC-6208 certificate to Apex Hospitals
    apex_idx, apex_org = apex_hospitals_org
    print(f"Adding correct MC-6208 certificate to: {apex_org.get('name')}")
    
    # Create the correct NABL certification
    correct_nabl_cert = {
        "name": "National Accreditation Board for Testing and Calibration Laboratories (NABL)",
        "type": "NABL Accreditation",
        "status": "Active",
        "certificate_number": "MC-6208",
        "test_categories": "Clinical Biochemistry",
        "issue_date": "15-12-2023",
        "expiry_date": "14-12-2025",
        "score_impact": 15.0,
        "source": "NABL PDF Document"
    }
    
    # Remove existing NABL certificates from Apex Hospitals
    certifications = apex_org.get('certifications', [])
    updated_certs = [c for c in certifications if not (isinstance(c, dict) and 'NABL' in c.get('type', ''))]
    
    # Add the correct certificate
    updated_certs.append(correct_nabl_cert)
    organizations[apex_idx]['certifications'] = updated_certs
    
    # Update data source
    data_source = apex_org.get('data_source', '')
    if 'NABL' not in data_source:
        if data_source:
            organizations[apex_idx]['data_source'] = data_source + '+NABL'
        else:
            organizations[apex_idx]['data_source'] = 'NABL'
    
    # Update quality indicators
    quality_indicators = apex_org.get('quality_indicators', {})
    if isinstance(quality_indicators, dict):
        quality_indicators['nabl_accredited'] = True
        quality_indicators['accreditation_valid'] = True
        organizations[apex_idx]['quality_indicators'] = quality_indicators
    
    # Update last_updated timestamp
    organizations[apex_idx]['last_updated'] = datetime.now().isoformat()
    
    # Save updated database
    try:
        with open('unified_healthcare_organizations.json', 'w', encoding='utf-8') as f:
            json.dump(organizations, f, indent=2, ensure_ascii=False)
        
        print("Database updated successfully!")
        print()
        
        # Verify the fix
        print("=== Verification ===")
        apex_org_updated = organizations[apex_idx]
        print(f"Organization: {apex_org_updated.get('name')}")
        print(f"Data Source: {apex_org_updated.get('data_source')}")
        
        total_score = 0
        nabl_found = False
        
        for cert in apex_org_updated.get('certifications', []):
            if isinstance(cert, dict):
                score_impact = cert.get('score_impact', 0)
                total_score += score_impact
                
                if 'NABL' in cert.get('type', ''):
                    nabl_found = True
                    print(f"✓ NABL Certificate: {cert.get('certificate_number')} (Score: {score_impact})")
                    print(f"  Status: {cert.get('status')}")
                    print(f"  Expiry: {cert.get('expiry_date')}")
        
        print(f"Total Score Impact: {total_score}")
        
        if nabl_found:
            print("✓ Fix applied successfully!")
        else:
            print("✗ Fix failed - NABL certificate not found")
        
    except Exception as e:
        print(f"Error saving database: {e}")

if __name__ == "__main__":
    fix_apex_nabl_certificate()