import sys
sys.path.append('.')
from streamlit_app import HealthcareOrgAnalyzer

# Test organizations
test_orgs = [
    "Apollo Hospitals Chennai",
    "Fortis Healthcare",
    "Max Healthcare",
    "AIIMS Delhi",
    "Mayo Clinic"
]

analyzer = HealthcareOrgAnalyzer()

print("Testing scoring system with multiple organizations:")
print("=" * 60)

for org_name in test_orgs:
    print(f"\nTesting: {org_name}")
    print("-" * 40)
    
    try:
        result = analyzer.search_organization_info(org_name)
        
        if result:
            print(f"✅ Total Score: {result['total_score']}")
            print(f"   Certification Score: {result['score_breakdown']['certification_score']}")
            print(f"   Quality Initiatives: {result['score_breakdown']['quality_initiatives_score']}")
            print(f"   Patient Feedback: {result['score_breakdown']['patient_feedback_score']}")
            print(f"   Active Certifications: {len(result['certifications'])}")
            
            # Show top certifications
            if result['certifications']:
                print("   Top Certifications:")
                for cert in result['certifications'][:3]:
                    print(f"     - {cert.get('name', 'Unknown')}: {cert.get('score_impact', 0)} points")
        else:
            print("❌ No data found")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

print("\n" + "=" * 60)
print("Testing completed!")