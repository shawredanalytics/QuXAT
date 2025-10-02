#!/usr/bin/env python3
"""
Fix duplicate Apex Hospitals entries in the unified database
Remove the entry with expired MC-5338 certificate, keep the one with active MC-6208
"""

import json
import os
from datetime import datetime

def fix_duplicate_apex_entries():
    """Remove duplicate Apex Hospitals entry with expired certificate"""
    
    print("=" * 80)
    print("FIXING DUPLICATE APEX HOSPITALS ENTRIES")
    print("=" * 80)
    
    # Load the database
    db_file = "unified_healthcare_organizations.json"
    if not os.path.exists(db_file):
        print(f"ERROR: Database file '{db_file}' not found!")
        return
    
    print(f"Loading database: {db_file}")
    
    try:
        with open(db_file, 'r', encoding='utf-8') as f:
            database = json.load(f)
        print(f"Database loaded with {len(database)} organizations")
    except Exception as e:
        print(f"ERROR loading database: {e}")
        return
    
    # Find all Apex Hospitals entries
    apex_entries = []
    apex_indices = []
    
    for i, org in enumerate(database):
        org_name = org.get('name', '').lower()
        original_name = org.get('original_name', '').lower()
        
        if 'apex hospitals' in org_name or 'apex hospitals' in original_name:
            apex_entries.append(org)
            apex_indices.append(i)
            print(f"\nFound Apex entry #{len(apex_entries)} at index {i}:")
            print(f"  Name: {org.get('name', 'N/A')}")
            print(f"  Original Name: {org.get('original_name', 'N/A')}")
            
            # Check NABL certificates
            certifications = org.get('certifications', [])
            nabl_certs = [cert for cert in certifications if 'NABL' in cert.get('type', '').upper()]
            
            for cert in nabl_certs:
                cert_num = cert.get('certificate_number', 'N/A')
                status = cert.get('status', 'N/A')
                expiry = cert.get('expiry_date', 'N/A')
                print(f"    NABL: {cert_num} | {status} | Expires: {expiry}")
    
    if len(apex_entries) < 2:
        print(f"Only {len(apex_entries)} Apex entries found. No duplicates to remove.")
        return
    
    print(f"\nFound {len(apex_entries)} Apex Hospitals entries")
    
    # Identify which entry to remove (the one with MC-5338)
    entry_to_remove = None
    remove_index = None
    
    for i, (entry, db_index) in enumerate(zip(apex_entries, apex_indices)):
        certifications = entry.get('certifications', [])
        
        for cert in certifications:
            if cert.get('certificate_number') == 'MC-5338':
                entry_to_remove = entry
                remove_index = db_index
                print(f"\nMarked for removal - Entry at index {db_index}:")
                print(f"  Name: {entry.get('name', 'N/A')}")
                print(f"  Has expired MC-5338 certificate")
                break
        
        if entry_to_remove:
            break
    
    if not entry_to_remove:
        print("No entry with MC-5338 certificate found!")
        return
    
    # Create backup
    backup_file = f"unified_healthcare_organizations_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    print(f"\nCreating backup: {backup_file}")
    
    try:
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        print("Backup created successfully")
    except Exception as e:
        print(f"ERROR creating backup: {e}")
        return
    
    # Remove the duplicate entry
    print(f"\nRemoving duplicate entry at index {remove_index}")
    del database[remove_index]
    
    print(f"Database now has {len(database)} organizations (removed 1)")
    
    # Save the updated database
    try:
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        print(f"Updated database saved to {db_file}")
    except Exception as e:
        print(f"ERROR saving database: {e}")
        return
    
    # Verify the fix
    print("\n" + "=" * 50)
    print("VERIFICATION")
    print("=" * 50)
    
    remaining_apex = []
    for org in database:
        org_name = org.get('name', '').lower()
        original_name = org.get('original_name', '').lower()
        
        if 'apex hospitals' in org_name or 'apex hospitals' in original_name:
            remaining_apex.append(org)
    
    print(f"Remaining Apex entries: {len(remaining_apex)}")
    
    for i, org in enumerate(remaining_apex, 1):
        print(f"\nApex Entry #{i}:")
        print(f"  Name: {org.get('name', 'N/A')}")
        print(f"  Original Name: {org.get('original_name', 'N/A')}")
        
        # Check NABL certificates
        certifications = org.get('certifications', [])
        nabl_certs = [cert for cert in certifications if 'NABL' in cert.get('type', '').upper()]
        
        for cert in nabl_certs:
            cert_num = cert.get('certificate_number', 'N/A')
            status = cert.get('status', 'N/A')
            expiry = cert.get('expiry_date', 'N/A')
            score = cert.get('score_impact', 0)
            print(f"    NABL: {cert_num} | {status} | Expires: {expiry} | Score: {score}")
            
            if cert_num == 'MC-6208':
                print(f"      ✓ CORRECT: Active MC-6208 certificate found!")
            elif cert_num == 'MC-5338':
                print(f"      ✗ ERROR: Expired MC-5338 still present!")
    
    print("\n" + "=" * 80)
    print("DUPLICATE REMOVAL COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    fix_duplicate_apex_entries()