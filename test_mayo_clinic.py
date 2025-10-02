#!/usr/bin/env python3
"""
Test script to investigate Mayo Clinic scoring issue
"""

import json
from streamlit_app import HealthcareOrgAnalyzer

def test_mayo_clinic():
    print("🏥 MAYO CLINIC SCORING INVESTIGATION")
    print("=" * 60)
    
    analyzer = HealthcareOrgAnalyzer()
    
    # Test 1: Search for Mayo Clinic
    print("\n1️⃣ SEARCH TEST")
    mayo_info = analyzer.search_organization_info('Mayo Clinic')
    print(f"Mayo Clinic Found: {mayo_info is not None}")
    
    if mayo_info:
        print(f"Mayo Clinic Info: {json.dumps(mayo_info, indent=2)}")
    else:
        print("❌ Mayo Clinic not found in search")
    
    # Test 2: Check database directly
    print("\n2️⃣ DATABASE CHECK")
    try:
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        mayo_entries = []
        for org in data['organizations']:
            org_name = org['name'].lower()
            if 'mayo' in org_name:
                mayo_entries.append(org['name'])
        
        if mayo_entries:
            print(f"✅ Found {len(mayo_entries)} Mayo-related entries:")
            for entry in mayo_entries:
                print(f"  - {entry}")
        else:
            print("❌ No Mayo-related entries found in database")
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
    
    # Test 3: Check JCI database specifically
    print("\n3️⃣ JCI DATABASE CHECK")
    try:
        with open('jci_accredited_organizations.json', 'r', encoding='utf-8') as f:
            jci_data = json.load(f)
        
        mayo_jci = []
        for org in jci_data:
            org_name = org['name'].lower()
            if 'mayo' in org_name:
                mayo_jci.append(org['name'])
        
        if mayo_jci:
            print(f"✅ Found {len(mayo_jci)} Mayo entries in JCI database:")
            for entry in mayo_jci:
                print(f"  - {entry}")
        else:
            print("❌ No Mayo entries found in JCI database")
            
    except Exception as e:
        print(f"❌ JCI database check failed: {e}")
    
    # Test 4: Check what happens with manual scoring
    print("\n4️⃣ MANUAL SCORING TEST")
    try:
        # Try to calculate score manually
        mayo_info = analyzer.search_organization_info('Mayo Clinic')
        if mayo_info:
            certifications = mayo_info.get('certifications', [])
            initiatives = mayo_info.get('quality_initiatives', [])
            score_data = analyzer.calculate_quality_score(certifications, initiatives, 'Mayo Clinic', None, [])
            mayo_score = score_data.get('total_score', 0)
            print(f"Mayo Clinic Manual Score: {mayo_score}")
            print(f"Score Breakdown: {score_data}")
            
            if mayo_score > 0:
                rankings = analyzer.calculate_organization_rankings('Mayo Clinic', mayo_score)
                print(f"Mayo Clinic Rankings: {rankings}")
            else:
                print("❌ Mayo Clinic received 0 score")
        else:
            print("❌ Cannot calculate score - Mayo Clinic not found")
            
    except Exception as e:
        print(f"❌ Manual scoring failed: {e}")
    
    # Test 5: Check search variations
    print("\n5️⃣ SEARCH VARIATIONS TEST")
    variations = [
        'Mayo Clinic',
        'Mayo Clinic Rochester',
        'Mayo Clinic - Rochester',
        'Mayo Medical Center',
        'Mayo Hospital'
    ]
    
    for variation in variations:
        result = analyzer.search_organization_info(variation)
        status = "✅ Found" if result else "❌ Not found"
        print(f"  {variation}: {status}")
    
    # Test 6: Check if it's a US hospital issue
    print("\n6️⃣ US HOSPITAL CHECK")
    us_hospitals = [
        'Johns Hopkins Hospital',
        'Cleveland Clinic',
        'Massachusetts General Hospital',
        'Mayo Clinic'
    ]
    
    for hospital in us_hospitals:
        result = analyzer.search_organization_info(hospital)
        status = "✅ Found" if result else "❌ Not found"
        print(f"  {hospital}: {status}")

if __name__ == "__main__":
    test_mayo_clinic()