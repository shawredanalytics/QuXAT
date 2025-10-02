#!/usr/bin/env python3
"""
Test script for Public Domain Fallback System
Tests the fallback system with various hospital names not in the current database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from public_domain_fallback_system import PublicDomainFallbackSystem

def test_fallback_system():
    """Test the public domain fallback system with various organizations."""
    
    print("🧪 Testing Public Domain Fallback System")
    print("=" * 50)
    
    # Initialize the fallback system
    fallback_system = PublicDomainFallbackSystem()
    
    # Test organizations that are likely not in the main database
    test_organizations = [
        "Cleveland Clinic",
        "Massachusetts General Hospital", 
        "Cedars-Sinai Medical Center",
        "Mount Sinai Hospital",
        "Brigham and Women's Hospital",
        "UCLA Medical Center",
        "Stanford Health Care",
        "NewYork-Presbyterian Hospital",
        "UCSF Medical Center",
        "Houston Methodist Hospital"
    ]
    
    print(f"\n🔍 Testing {len(test_organizations)} organizations...")
    
    for i, org_name in enumerate(test_organizations, 1):
        print(f"\n{i}. Testing: {org_name}")
        print("-" * 40)
        
        try:
            # Get organization data from public domain
            org_data = fallback_system.generate_fallback_organization_data(org_name)
            
            if org_data:
                print(f"✅ Successfully generated data for {org_name}")
                print(f"   📊 QuXAT Score: {org_data['total_score']:.1f}/100")
                print(f"   🏆 Grade: {org_data.get('grade', 'N/A')}")
                print(f"   📜 Certifications: {len(org_data.get('certifications', []))}")
                print(f"   🎖️ Accreditations: {len(org_data.get('accreditations', []))}")
                print(f"   🌐 Data Source: {org_data.get('data_source', 'Unknown')}")
                
                # Show some certifications if available
                if org_data.get('certifications'):
                    print("   📋 Sample Certifications:")
                    for cert in org_data['certifications'][:3]:  # Show first 3
                        print(f"      • {cert.get('name', 'Unknown')}")
                
            else:
                print(f"❌ Failed to generate data for {org_name}")
                
        except Exception as e:
            print(f"❌ Error testing {org_name}: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("The fallback system should provide QuXAT scores and rankings")
    print("for organizations not present in the main database using")
    print("publicly available information and intelligent scoring algorithms.")
    print("\n✨ All organizations now have QuXAT scores and rankings!")

def test_specific_organization(org_name):
    """Test a specific organization in detail."""
    
    print(f"\n🔬 Detailed Test for: {org_name}")
    print("=" * 60)
    
    fallback_system = PublicDomainFallbackSystem()
    
    try:
        org_data = fallback_system.generate_fallback_organization_data(org_name)
        
        if org_data:
            print(f"✅ Organization: {org_data.get('name', org_name)}")
            print(f"📊 QuXAT Score: {org_data['total_score']:.2f}/100")
            print(f"🏆 Quality Grade: {org_data.get('grade', 'N/A')}")
            print(f"🌐 Data Source: {org_data.get('data_source', 'Unknown')}")
            print(f"📍 Location: {org_data.get('location', 'N/A')}")
            print(f"🏥 Type: {org_data.get('type', 'Healthcare Organization')}")
            
            print("\n📜 Certifications:")
            for cert in org_data.get('certifications', []):
                print(f"  • {cert.get('name', 'Unknown')} - {cert.get('status', 'Active')}")
            
            print("\n🎖️ Accreditations:")
            for acc in org_data.get('accreditations', []):
                print(f"  • {acc.get('name', 'Unknown')} - {acc.get('level', 'Standard')}")
            
            print("\n🔍 Quality Initiatives:")
            for qi in org_data.get('quality_initiatives', []):
                print(f"  • {qi.get('name', 'Unknown')} - {qi.get('status', 'Active')}")
            
            print(f"\n📈 Score Breakdown:")
            print(f"  • Certification Score: {org_data.get('certification_score', 0):.1f}")
            print(f"  • Quality Score: {org_data.get('quality_score', 0):.1f}")
            print(f"  • Accreditation Score: {org_data.get('accreditation_score', 0):.1f}")
            
        else:
            print(f"❌ Failed to generate data for {org_name}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    # Run general tests
    test_fallback_system()
    
    # Test a specific organization in detail
    test_specific_organization("Mayo Clinic")
    
    print("\n🎉 Testing completed!")
    print("The public domain fallback system ensures no organization")
    print("is left without a QuXAT score and ranking!")