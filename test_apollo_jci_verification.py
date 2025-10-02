#!/usr/bin/env python3
"""
Test script to verify JCI accreditation status for Apollo Hospitals locations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import HealthcareOrgAnalyzer

def test_apollo_jci_status():
    """Test JCI accreditation status for Apollo Hospitals locations"""
    
    print("🔍 Testing JCI Accreditation Status for Apollo Hospitals")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = HealthcareOrgAnalyzer()
    
    # Test locations
    locations = [
        "Apollo Hospitals Hyderabad",
        "Apollo Hospitals Secunderabad",
        "Apollo Hospital Hyderabad",
        "Apollo Hospital Secunderabad"
    ]
    
    results = {}
    
    for location in locations:
        print(f"\n🏥 Searching for: {location}")
        print("-" * 40)
        
        try:
            # Search for the organization
            org_data = analyzer.search_organization_info(location)
            
            if org_data and isinstance(org_data, dict):
                print(f"✅ Found data for: {org_data.get('name', location)}")
                
                # Check certifications
                certifications = org_data.get('certifications', [])
                jci_found = False
                jci_details = []
                
                for cert in certifications:
                    if isinstance(cert, dict):
                        cert_name = cert.get('name', '').lower()
                        if 'jci' in cert_name or 'joint commission international' in cert_name:
                            jci_found = True
                            jci_details.append({
                                'name': cert.get('name', ''),
                                'status': cert.get('status', ''),
                                'valid_until': cert.get('valid_until', ''),
                                'score': cert.get('score', 0)
                            })
                
                # Store results
                results[location] = {
                    'found': True,
                    'org_name': org_data.get('name', location),
                    'jci_accredited': jci_found,
                    'jci_details': jci_details,
                    'total_certifications': len(certifications),
                    'total_score': org_data.get('total_score', 0)
                }
                
                # Print JCI status
                if jci_found:
                    print(f"🏆 JCI ACCREDITED: YES")
                    for detail in jci_details:
                        print(f"   - {detail['name']}")
                        print(f"     Status: {detail['status']}")
                        if detail['valid_until']:
                            print(f"     Valid Until: {detail['valid_until']}")
                        print(f"     Score: {detail['score']}")
                else:
                    print(f"❌ JCI ACCREDITED: NO")
                
                print(f"📊 Total Score: {org_data.get('total_score', 0)}")
                print(f"📋 Total Certifications: {len(certifications)}")
                
            else:
                print(f"❌ No data found for: {location}")
                results[location] = {
                    'found': False,
                    'jci_accredited': False,
                    'jci_details': [],
                    'total_certifications': 0,
                    'total_score': 0
                }
                
        except Exception as e:
            print(f"❌ Error searching for {location}: {str(e)}")
            results[location] = {
                'found': False,
                'error': str(e),
                'jci_accredited': False,
                'jci_details': [],
                'total_certifications': 0,
                'total_score': 0
            }
    
    # Summary comparison
    print("\n" + "=" * 60)
    print("📊 SUMMARY COMPARISON")
    print("=" * 60)
    
    for location, data in results.items():
        if data['found']:
            status = "✅ JCI ACCREDITED" if data['jci_accredited'] else "❌ NOT JCI ACCREDITED"
            print(f"{location}: {status}")
            if data['jci_details']:
                for detail in data['jci_details']:
                    print(f"   └─ {detail['name']} (Score: {detail['score']})")
        else:
            print(f"{location}: ❌ NOT FOUND IN DATABASE")
    
    return results

if __name__ == "__main__":
    results = test_apollo_jci_status()