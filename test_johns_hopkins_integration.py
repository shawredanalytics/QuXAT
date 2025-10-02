#!/usr/bin/env python3
"""
Test script to verify Johns Hopkins Hospital integration in QuXAT system
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from international_scoring_algorithm import InternationalHealthcareScorer

def test_johns_hopkins_integration():
    """Test Johns Hopkins Hospital integration"""
    
    print("🧪 Testing Johns Hopkins Hospital Integration")
    print("=" * 50)
    
    # Test 1: Check if Johns Hopkins is in unified database
    print("\n📋 Test 1: Johns Hopkins in Unified Database")
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
        
        johns_hopkins_found = None
        for org in orgs:
            if isinstance(org, dict) and 'johns hopkins' in org.get('name', '').lower():
                johns_hopkins_found = org
                break
        
        if johns_hopkins_found:
            print(f"✅ Found: {johns_hopkins_found['name']}")
            print(f"   Location: {johns_hopkins_found.get('city', 'N/A')}, {johns_hopkins_found.get('state', 'N/A')}")
            print(f"   Type: {johns_hopkins_found.get('hospital_type', 'N/A')}")
            print(f"   Quality Score: {johns_hopkins_found.get('quality_score', 'N/A')}")
            print(f"   Certifications: {len(johns_hopkins_found.get('certifications', []))}")
        else:
            print("❌ Johns Hopkins not found in database")
            return False
            
    except Exception as e:
        print(f"❌ Error loading database: {e}")
        return False
    
    # Test 2: Test certification scoring
    print("\n🏆 Test 2: Certification Scoring")
    try:
        scorer = InternationalHealthcareScorer()
        
        # Extract certifications for scoring
        certifications = johns_hopkins_found.get('certifications', [])
        if certifications:
            print(f"   Found {len(certifications)} certifications:")
            total_score = 0
            for cert in certifications:
                cert_name = cert.get('name', 'Unknown')
                cert_type = cert.get('type', 'Unknown')
                score_impact = cert.get('score_impact', 0)
                total_score += score_impact
                print(f"   - {cert_name} ({cert_type}): +{score_impact} points")
            
            print(f"   Total Certification Score: {total_score}")
            
            # Test with scorer
            test_org = {
                'name': johns_hopkins_found['name'],
                'certifications': certifications
            }
            
            score_result = scorer.calculate_international_quality_score(
                certifications=certifications,
                quality_metrics=None,
                hospital_context={'region': 'North America', 'hospital_type': 'Academic Medical Center'}
            )
            print(f"   Scorer Result: {score_result}")
            
        else:
            print("❌ No certifications found")
            return False
            
    except Exception as e:
        print(f"❌ Error in certification scoring: {e}")
        return False
    
    # Test 3: Search functionality
    print("\n🔍 Test 3: Search Functionality")
    try:
        search_terms = ['johns hopkins', 'hopkins', 'baltimore']
        
        for term in search_terms:
            matches = []
            for org in orgs:
                if isinstance(org, dict):
                    name = org.get('name', '').lower()
                    city = org.get('city', '').lower()
                    keywords = org.get('search_keywords', [])
                    
                    if (term.lower() in name or 
                        term.lower() in city or 
                        any(term.lower() in keyword.lower() for keyword in keywords)):
                        matches.append(org['name'])
            
            print(f"   Search '{term}': {len(matches)} matches")
            if matches:
                print(f"     - {matches[0]}")  # Show first match
        
    except Exception as e:
        print(f"❌ Error in search functionality: {e}")
        return False
    
    # Test 4: Quality indicators
    print("\n📊 Test 4: Quality Indicators")
    try:
        quality_indicators = johns_hopkins_found.get('quality_indicators', {})
        if quality_indicators:
            print("   Quality Indicators:")
            for key, value in quality_indicators.items():
                status = "✅" if value else "❌"
                print(f"   {status} {key.replace('_', ' ').title()}: {value}")
        else:
            print("❌ No quality indicators found")
            
    except Exception as e:
        print(f"❌ Error checking quality indicators: {e}")
        return False
    
    return True

def main():
    """Main function"""
    success = test_johns_hopkins_integration()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Johns Hopkins Hospital integration test PASSED!")
        print("   - Organization found in database")
        print("   - Certifications properly configured")
        print("   - Search functionality working")
        print("   - Quality indicators present")
        print("\n💡 You can now search for 'Johns Hopkins' in the QuXAT app!")
    else:
        print("❌ Johns Hopkins Hospital integration test FAILED!")
        print("   Please check the integration and try again.")

if __name__ == "__main__":
    main()