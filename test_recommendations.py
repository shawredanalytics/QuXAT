#!/usr/bin/env python3
"""
Test script for the improvement recommendations feature
"""

from streamlit_app import HealthcareOrgAnalyzer

def test_recommendations():
    """Test the recommendation system with various healthcare organizations"""
    
    analyzer = HealthcareOrgAnalyzer()
    
    test_organizations = [
        "Apollo Hospitals Chennai",
        "Fortis Healthcare",
        "Max Healthcare",
        "AIIMS Delhi"
    ]
    
    print("🧪 Testing Improvement Recommendations System")
    print("=" * 50)
    
    for org_name in test_organizations:
        print(f"\n🏥 Testing: {org_name}")
        print("-" * 30)
        
        try:
            result = analyzer.search_organization_info(org_name)
            
            if result and 'improvement_recommendations' in result:
                print("✅ Recommendations generated successfully!")
                print(f"📊 Score: {result.get('total_score', 0):.1f}/100")
                
                recs = result['improvement_recommendations']
                
                # Display recommendation counts
                print(f"🚀 Priority Actions: {len(recs.get('priority_actions', []))}")
                print(f"📜 Certification Gaps: {len(recs.get('certification_gaps', []))}")
                print(f"⭐ Quality Initiatives: {len(recs.get('quality_initiatives', []))}")
                print(f"⚙️ Operational Improvements: {len(recs.get('operational_improvements', []))}")
                print(f"🎯 Strategic Recommendations: {len(recs.get('strategic_recommendations', []))}")
                
                # Display score potential
                score_potential = recs.get('score_potential', {})
                if score_potential:
                    current = score_potential.get('current_score', 0)
                    improvement = score_potential.get('improvement_potential', 0)
                    print(f"📈 Improvement Potential: +{improvement:.1f} points")
                
                # Show sample priority action
                priority_actions = recs.get('priority_actions', [])
                if priority_actions:
                    action = priority_actions[0]
                    print(f"💡 Top Priority: {action.get('action', 'N/A')} ({action.get('impact', 'N/A')} Impact)")
                
            else:
                print("❌ Failed to generate recommendations")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Recommendation system testing completed!")

if __name__ == "__main__":
    test_recommendations()