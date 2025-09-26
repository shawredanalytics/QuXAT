"""
Test script for full JCI integration with the QuXAT Healthcare Quality Grid scoring system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from streamlit_app import HealthcareOrgAnalyzer

def test_full_integration():
    print("🧪 Testing Full JCI Integration with QuXAT Healthcare Quality Grid Scoring System...")
    
    # Initialize analyzer
    analyzer = HealthcareOrgAnalyzer()
    
    # Test organizations with different JCI statuses
    test_organizations = [
        "Singapore General Hospital",  # JCI accredited
        "Apollo Hospitals",           # JCI accredited (partial match)
        "Mayo Clinic",               # Not in JCI database
        "Cleveland Clinic"           # Not in JCI database
    ]
    
    for org_name in test_organizations:
        print(f"\n{'='*60}")
        print(f"🏥 Testing: {org_name}")
        print(f"{'='*60}")
        
        # Search for certifications
        certifications = analyzer.search_certifications(org_name)
        
        if certifications:
            print(f"✅ Found {len(certifications)} certifications:")
            for cert in certifications:
                print(f"   - {cert.get('name', 'Unknown')}: {cert.get('status', 'Unknown')} ({cert.get('score_impact', 0)} points)")
                if cert.get('name') == 'JCI' and 'organization_info' in cert:
                    org_info = cert['organization_info']
                    print(f"     🌟 JCI Details: {org_info.get('country', 'N/A')}, Accredited: {org_info.get('accreditation_date', 'N/A')}")
            
            # Calculate quality score with patient feedback
            initiatives = [
                {'name': 'Patient Safety Initiative', 'impact_score': 8},
                {'name': 'Digital Health Program', 'impact_score': 6}
            ]
            
            # Sample patient feedback data for testing
            patient_feedback_data = [
                {
                    'organization_name': org_name,
                    'patient_id': 'P001',
                    'category': 'overall_experience',
                    'rating': 4,
                    'visit_date': '2024-01-15',
                    'department': 'Cardiology',
                    'feedback_text': 'Excellent care and professional staff. Very satisfied with the treatment.'
                },
                {
                    'organization_name': org_name,
                    'patient_id': 'P002',
                    'category': 'staff_behavior',
                    'rating': 5,
                    'visit_date': '2024-01-20',
                    'department': 'Emergency',
                    'feedback_text': 'Outstanding service, doctors were very caring and explained everything clearly.'
                },
                {
                    'organization_name': org_name,
                    'patient_id': 'P003',
                    'category': 'facility_quality',
                    'rating': 3,
                    'visit_date': '2024-01-25',
                    'department': 'Orthopedics',
                    'feedback_text': 'Good treatment but waiting time was too long. Facilities could be better.'
                }
            ]
            
            score_breakdown = analyzer.calculate_quality_score(certifications, initiatives, org_name, None, patient_feedback_data)
            
            print(f"\n📊 Quality Score Breakdown:")
            print(f"   - Certification Score: {score_breakdown['certification_score']}/45")
            print(f"   - Initiative Score: {score_breakdown['initiative_score']}/15")
            print(f"   - Transparency Score: {score_breakdown['transparency_score']}/10")
            print(f"   - Patient Feedback Score: {score_breakdown['patient_feedback_score']}/15")
            print(f"   - Reputation Bonus: {score_breakdown['reputation_bonus']}/10")
            print(f"   - Location Adjustment: {score_breakdown['location_adjustment']}/5")
            print(f"   - TOTAL SCORE: {score_breakdown['total_score']}/85")
            
            # Determine grade (normalized to 100-point scale)
            total_score = score_breakdown['total_score']
            normalized_score = (total_score / 85) * 100  # Convert from 85-point to 100-point scale
            
            if normalized_score >= 90:
                grade = "A+"
            elif normalized_score >= 80:
                grade = "A"
            elif normalized_score >= 70:
                grade = "B+"
            elif normalized_score >= 60:
                grade = "B"
            elif normalized_score >= 50:
                grade = "C"
            else:
                grade = "F"
            
            print(f"   - NORMALIZED SCORE: {normalized_score:.1f}/100")
            print(f"   - GRADE: {grade}")
            
        else:
            print("❌ No certifications found")
    
    print(f"\n{'='*60}")
    print("🎉 Full Integration Test Completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_full_integration()