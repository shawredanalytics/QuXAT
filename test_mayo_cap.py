#!/usr/bin/env python3
"""
Test script to check Mayo Clinic's CAP accreditation in QuXAT scoring
"""

import sys
import os
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import HealthcareOrgAnalyzer

def test_mayo_clinic_cap():
    """Test Mayo Clinic's CAP accreditation status and scoring"""
    
    # Initialize analyzer
    analyzer = HealthcareOrgAnalyzer()
    
    print("🔍 Testing Mayo Clinic's CAP Accreditation Status")
    print("=" * 60)
    
    # Search for Mayo Clinic
    print("Searching for Mayo Clinic in the database...")
    mayo_info = analyzer.search_organization_info('Mayo Clinic')
    
    if mayo_info:
        print(f"✅ Found: {mayo_info.get('name', 'Unknown')}")
        print(f"🌍 Country: {mayo_info.get('country', 'Unknown')}")
        
        # Check certifications
        certifications = mayo_info.get('certifications', [])
        print(f"\n📋 Certifications ({len(certifications)} total):")
        
        cap_found = False
        for i, cert in enumerate(certifications, 1):
            cert_name = cert.get('name', 'Unknown')
            cert_status = cert.get('status', 'Unknown')
            print(f"  {i}. {cert_name} - Status: {cert_status}")
            
            if 'CAP' in cert_name.upper():
                print(f"     🎯 *** CAP CERTIFICATION FOUND ***")
                cap_found = True
        
        if not cap_found:
            print("  ❌ No CAP certifications found in Mayo Clinic's profile")
        
        # Calculate score
        initiatives = mayo_info.get('quality_initiatives', [])
        score_result = analyzer.calculate_quality_score(certifications, initiatives, 'Mayo Clinic')
        
        print(f"\n📊 QuXAT Score Breakdown:")
        print(f"  Certification Score: {score_result.get('certification_score', 0)}")
        print(f"  Quality Initiatives Score: {score_result.get('quality_initiatives_score', 0)}")
        print(f"  Total Score: {score_result.get('total_score', 0)}")
        
        # Check certification breakdown
        cert_breakdown = score_result.get('certification_breakdown', {})
        print(f"\n🔍 Certification Type Breakdown:")
        if cert_breakdown:
            for cert_type, details in cert_breakdown.items():
                count = details.get('count', 0)
                total_score = details.get('total_score', 0)
                description = details.get('description', 'No description')
                print(f"  {cert_type}: {count} certs, {total_score:.1f} points")
                print(f"    Description: {description}")
        else:
            print("  No certification breakdown available")
            
        # Check if CAP is in the breakdown
        if 'CAP' in cert_breakdown:
            print(f"\n✅ CAP certification IS being counted in the score!")
            cap_details = cert_breakdown['CAP']
            print(f"   CAP Score Contribution: {cap_details.get('total_score', 0):.1f} points")
        else:
            print(f"\n❌ CAP certification is NOT being counted in the score!")
            
    else:
        print("❌ Mayo Clinic not found in database")
    
    print("\n" + "=" * 60)
    print("🔍 Now checking CAP laboratories database...")
    
    # Check CAP laboratories database
    try:
        with open('cap_laboratories.json', 'r', encoding='utf-8') as f:
            cap_data = json.load(f)
            
        mayo_cap_entries = []
        for entry in cap_data:
            if 'mayo clinic' in entry.get('name', '').lower():
                mayo_cap_entries.append(entry)
        
        print(f"📋 Found {len(mayo_cap_entries)} Mayo Clinic entries in CAP database:")
        for i, entry in enumerate(mayo_cap_entries, 1):
            print(f"  {i}. {entry.get('name', 'Unknown')}")
            print(f"     Accreditation: {entry.get('accreditation_type', 'Unknown')}")
            print(f"     Status: {entry.get('status', 'Unknown')}")
            
    except FileNotFoundError:
        print("❌ CAP laboratories database file not found")
    except Exception as e:
        print(f"❌ Error reading CAP database: {str(e)}")

if __name__ == "__main__":
    test_mayo_clinic_cap()