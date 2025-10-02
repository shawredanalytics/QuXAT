#!/usr/bin/env python3
"""
Test script to verify QuXAT score generation for Johns Hopkins
"""

from public_domain_fallback_system import PublicDomainFallbackSystem
import json

def test_johns_hopkins_quxat_score():
    """Test QuXAT score generation for Johns Hopkins"""
    print("=" * 60)
    print("🏥 JOHNS HOPKINS QUXAT SCORE TEST")
    print("=" * 60)
    
    # Initialize the fallback system
    system = PublicDomainFallbackSystem()
    
    # Test variations of Johns Hopkins name
    test_names = [
        "Johns Hopkins",
        "John Hopkins", 
        "Johns Hopkins Hospital",
        "Johns Hopkins Medical Center"
    ]
    
    for name in test_names:
        print(f"\n🔍 Testing: {name}")
        print("-" * 40)
        
        try:
            # Generate fallback data
            result = system.generate_fallback_organization_data(name)
            
            # Display results
            print(f"✅ Organization: {result['name']}")
            print(f"📊 QuXAT Score: {result['quality_score']}/100")
            print(f"🎯 Total Score: {result['total_score']}/100")
            print(f"🌐 Data Source: {result['data_source']}")
            print(f"📜 Certifications: {len(result['certifications'])}")
            print(f"🔒 Confidence Level: {result['confidence_level']}")
            print(f"⚠️  Fallback Notice: {result['fallback_notice']}")
            
            # Show score breakdown
            if 'score_breakdown' in result:
                print(f"📈 Score Breakdown:")
                for key, value in result['score_breakdown'].items():
                    print(f"   • {key}: {value}")
                    
        except Exception as e:
            print(f"❌ Error testing {name}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 Johns Hopkins QuXAT Score Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_johns_hopkins_quxat_score()