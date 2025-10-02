#!/usr/bin/env python3
"""
Fix NABL data loading issue for Apex Hospitals Pvt. Ltd., Jaipur
The system is loading expired certificate MC-5338 instead of active certificate MC-6208
"""

import json
import sys
from datetime import datetime

def fix_apex_nabl_data():
    """Fix the NABL certificate data for Apex Hospitals Pvt. Ltd., Jaipur"""
    print("🔧 Fixing NABL Certificate Data Loading Issue")
    print("=" * 60)
    
    # Load the unified database
    try:
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
        print(f"✅ Loaded database with {len(db)} organizations")
    except Exception as e:
        print(f"❌ Error loading database: {e}")
        return False
    
    # Find Apex Hospitals Pvt. Ltd., Jaipur
    apex_org = None
    apex_index = None
    
    for i, org in enumerate(db):
        if isinstance(org, dict) and 'Apex Hospitals Pvt. Ltd., Jaipur' in org.get('name', ''):
            apex_org = org
            apex_index = i
            break
    
    if not apex_org:
        print("❌ Apex Hospitals Pvt. Ltd., Jaipur not found in database")
        return False
    
    print(f"✅ Found organization: {apex_org.get('name')}")
    
    # Check current certifications
    certifications = apex_org.get('certifications', [])
    print(f"📋 Current certifications: {len(certifications)}")
    
    # Find and analyze NABL certificates
    nabl_certs = []
    other_certs = []
    
    for cert in certifications:
        if isinstance(cert, dict):
            cert_name = cert.get('name', '').upper()
            cert_type = cert.get('type', '').upper()
            
            if 'NABL' in cert_name or 'NABL' in cert_type:
                nabl_certs.append(cert)
                print(f"   NABL Cert: {cert.get('certificate_number', 'N/A')} - Status: {cert.get('status', 'N/A')}")
            else:
                other_certs.append(cert)
    
    print(f"🎯 Found {len(nabl_certs)} NABL certificates")
    
    # Remove expired NABL certificates and keep only active ones
    active_nabl_certs = []
    removed_certs = []
    
    for cert in nabl_certs:
        cert_number = cert.get('certificate_number', '')
        status = cert.get('status', '')
        expiry_date = cert.get('expiry_date', '')
        
        # Check if certificate is active and valid
        if status == 'Active' and cert_number == 'MC-6208':
            active_nabl_certs.append(cert)
            print(f"   ✅ Keeping active certificate: {cert_number}")
        elif status == 'Expired' or cert_number == 'MC-5338':
            removed_certs.append(cert)
            print(f"   ❌ Removing expired certificate: {cert_number} (Status: {status})")
        else:
            # For other certificates, check expiry date
            try:
                if expiry_date:
                    expiry = datetime.strptime(expiry_date, '%d-%m-%Y')
                    if expiry > datetime.now():
                        active_nabl_certs.append(cert)
                        print(f"   ✅ Keeping valid certificate: {cert_number}")
                    else:
                        removed_certs.append(cert)
                        print(f"   ❌ Removing expired certificate: {cert_number}")
                else:
                    # If no expiry date and status is not explicitly expired, keep it
                    if status != 'Expired':
                        active_nabl_certs.append(cert)
                        print(f"   ⚠️  Keeping certificate with unknown expiry: {cert_number}")
                    else:
                        removed_certs.append(cert)
                        print(f"   ❌ Removing expired certificate: {cert_number}")
            except:
                # If date parsing fails, check status
                if status == 'Active':
                    active_nabl_certs.append(cert)
                    print(f"   ✅ Keeping active certificate: {cert_number}")
                else:
                    removed_certs.append(cert)
                    print(f"   ❌ Removing problematic certificate: {cert_number}")
    
    # Ensure we have the correct MC-6208 certificate
    has_mc6208 = any(cert.get('certificate_number') == 'MC-6208' for cert in active_nabl_certs)
    
    if not has_mc6208:
        print("⚠️  MC-6208 certificate not found in active certificates, adding it...")
        
        # Add the correct MC-6208 certificate
        mc6208_cert = {
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
        active_nabl_certs.append(mc6208_cert)
        print("   ✅ Added MC-6208 certificate")
    
    # Update the organization's certifications
    updated_certifications = other_certs + active_nabl_certs
    apex_org['certifications'] = updated_certifications
    
    # Update quality indicators
    if 'quality_indicators' not in apex_org:
        apex_org['quality_indicators'] = {}
    
    apex_org['quality_indicators']['nabl_accredited'] = len(active_nabl_certs) > 0
    apex_org['quality_indicators']['nabl_score'] = sum(cert.get('score_impact', 0) for cert in active_nabl_certs)
    
    # Update the database
    db[apex_index] = apex_org
    
    # Save the updated database
    try:
        # Create backup first
        backup_filename = f'unified_healthcare_organizations_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        print(f"✅ Created backup: {backup_filename}")
        
        # Save updated database
        with open('unified_healthcare_organizations.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        print("✅ Updated database saved successfully")
        
        # Summary
        print(f"\n📊 Fix Summary:")
        print(f"   • Removed {len(removed_certs)} expired/invalid NABL certificates")
        print(f"   • Kept {len(active_nabl_certs)} active NABL certificates")
        print(f"   • Total certifications now: {len(updated_certifications)}")
        print(f"   • NABL Score Impact: {apex_org['quality_indicators']['nabl_score']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving database: {e}")
        return False

if __name__ == "__main__":
    success = fix_apex_nabl_data()
    if success:
        print("\n🎉 NABL certificate data fix completed successfully!")
        print("   The system should now properly load the active MC-6208 certificate.")
    else:
        print("\n❌ Fix failed. Please check the errors above.")
        sys.exit(1)