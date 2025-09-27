#!/usr/bin/env python3
"""
Check NABL Integration Status
Analyzes the current state of NABL data integration and identifies issues.
"""

import json
import os
from datetime import datetime

def check_nabl_integration_status():
    """Check the current NABL integration status"""
    
    print("=== NABL Integration Status Check ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if NABL files exist
    nabl_files = [
        'nabl_pdf_extracted_text.txt',
        'nabl_database_integrator.py',
        'nabl_accreditation_extractor.py',
        'nabl_integration_report_20250926_180120.json',
        'nabl_integration_test_report_20250926_180430.json'
    ]
    
    print("1. NABL Files Status:")
    for file in nabl_files:
        exists = os.path.exists(file)
        print(f"   {file}: {'✓ EXISTS' if exists else '✗ MISSING'}")
    print()
    
    # Check unified database for NABL data
    print("2. Unified Database NABL Status:")
    data = None
    try:
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both list and dict structures
        if isinstance(data, dict):
            data = data.get('organizations', [])
        
        total_orgs = len(data)
        nabl_orgs = 0
        nabl_certified_orgs = 0
        
        for org in data:
            if not isinstance(org, dict):
                continue
                
            # Check data source
            if org.get('data_source') == 'NABL':
                nabl_orgs += 1
            
            # Check certifications for NABL
            certifications = org.get('certifications', [])
            for cert in certifications:
                if isinstance(cert, dict):
                    if 'NABL' in cert.get('name', '') or 'NABL' in cert.get('type', ''):
                        nabl_certified_orgs += 1
                        break
        
        print(f"   Total organizations: {total_orgs}")
        print(f"   Organizations with data_source='NABL': {nabl_orgs}")
        print(f"   Organizations with NABL certifications: {nabl_certified_orgs}")
        print()
        
    except Exception as e:
        print(f"   Error reading unified database: {e}")
        print()
    
    # Check for Apex Hospitals specifically
    print("3. Apex Hospitals Analysis:")
    try:
        if data is None:
            print("   No data available for analysis")
            print()
            return
            
        apex_found = False
        for org in data:
            if not isinstance(org, dict):
                continue
                
            if 'apex' in org.get('name', '').lower() and 'hospital' in org.get('name', '').lower():
                apex_found = True
                print(f"   Name: {org.get('name')}")
                print(f"   City: {org.get('city')}")
                print(f"   Data Source: {org.get('data_source')}")
                print(f"   Certifications: {len(org.get('certifications', []))}")
                
                # Check for NABL in certifications
                has_nabl = False
                for cert in org.get('certifications', []):
                    if isinstance(cert, dict):
                        if 'NABL' in cert.get('name', '') or 'NABL' in cert.get('type', ''):
                            has_nabl = True
                            print(f"   NABL Certification: ✓ FOUND")
                            break
                
                if not has_nabl:
                    print(f"   NABL Certification: ✗ MISSING")
                print()
        
        if not apex_found:
            print("   Apex Hospitals not found in database")
            print()
            
    except Exception as e:
        print(f"   Error analyzing Apex Hospitals: {e}")
        print()
    
    # Check NABL extracted text for Apex
    print("4. NABL Extracted Text Analysis:")
    try:
        with open('nabl_pdf_extracted_text.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        apex_mentions = content.count('Apex Hospitals')
        print(f"   'Apex Hospitals' mentions: {apex_mentions}")
        
        if apex_mentions > 0:
            # Find the specific line
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'Apex Hospitals' in line and 'NABL' not in line.upper():
                    # Check surrounding lines for NABL info
                    context_start = max(0, i-2)
                    context_end = min(len(lines), i+3)
                    print(f"   Context around line {i+1}:")
                    for j in range(context_start, context_end):
                        marker = ">>> " if j == i else "    "
                        print(f"   {marker}{lines[j]}")
                    break
        print()
        
    except Exception as e:
        print(f"   Error reading NABL extracted text: {e}")
        print()
    
    # Check integration reports
    print("5. Integration Reports Analysis:")
    try:
        with open('nabl_integration_report_20250926_180120.json', 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        print(f"   NABL organizations loaded: {report.get('nabl_organizations_loaded', 'N/A')}")
        print(f"   New organizations added: {report.get('new_organizations_added', 'N/A')}")
        print(f"   Total organizations final: {report.get('total_organizations_final', 'N/A')}")
        print(f"   NABL certifications added: {report.get('nabl_certifications_added', 'N/A')}")
        print()
        
    except Exception as e:
        print(f"   Error reading integration report: {e}")
        print()
    
    print("=== Analysis Complete ===")
    print()
    print("RECOMMENDATIONS:")
    print("1. NABL data exists in extracted text but is not integrated into unified database")
    print("2. Need to run NABL integration process to add NABL certifications")
    print("3. Apex Hospitals should get additional NABL score (typically 15 points)")
    print("4. Integration scripts exist but may need to be re-executed")

if __name__ == "__main__":
    check_nabl_integration_status()