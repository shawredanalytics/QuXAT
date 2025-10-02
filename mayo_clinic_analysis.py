#!/usr/bin/env python3
"""
Mayo Clinic QuXAT Scoring Analysis
Detailed investigation of why Mayo Clinic receives a low score
"""

import json
import os
os.environ['STREAMLIT_LOGGER_LEVEL'] = 'ERROR'

from streamlit_app import HealthcareOrgAnalyzer

def analyze_mayo_clinic():
    print("🏥 MAYO CLINIC QuXAT SCORING ANALYSIS")
    print("=" * 60)
    
    analyzer = HealthcareOrgAnalyzer()
    
    # Get Mayo Clinic data
    mayo_info = analyzer.search_organization_info('Mayo Clinic')
    
    if not mayo_info:
        print("❌ Mayo Clinic not found in system")
        return
    
    print("✅ Mayo Clinic found in system")
    print(f"📊 Total QuXAT Score: {mayo_info.get('total_score', 0)}")
    
    # Analyze score breakdown
    score_breakdown = mayo_info.get('score_breakdown', {})
    
    print("\n📋 DETAILED SCORE BREAKDOWN:")
    print("-" * 40)
    
    # Certification Score
    cert_score = score_breakdown.get('certification_score', 0)
    print(f"🏆 Certification Score: {cert_score}")
    
    cert_breakdown = score_breakdown.get('certification_breakdown', {})
    if cert_breakdown:
        for cert_type, details in cert_breakdown.items():
            print(f"  • {cert_type}: {details.get('total_score', 0)} points")
            print(f"    - Count: {details.get('count', 0)}")
            print(f"    - Weight: {details.get('weight', 0)}")
    
    # Quality Initiatives Score
    quality_score = score_breakdown.get('quality_initiatives_score', 0)
    print(f"\n🎯 Quality Initiatives Score: {quality_score}")
    
    # Patient Feedback Score
    feedback_score = score_breakdown.get('patient_feedback_score', 0)
    print(f"👥 Patient Feedback Score: {feedback_score}")
    
    # Compliance Check
    compliance = score_breakdown.get('compliance_check', {})
    if compliance:
        print(f"\n⚖️ COMPLIANCE ANALYSIS:")
        print(f"  • Total Required Standards: {compliance.get('total_required', 0)}")
        print(f"  • Compliant Count: {compliance.get('compliant_count', 0)}")
        print(f"  • Non-Compliant Count: {compliance.get('non_compliant_count', 0)}")
        print(f"  • Compliance Percentage: {compliance.get('compliance_percentage', 0):.1f}%")
        print(f"  • Fully Compliant: {'✅ Yes' if compliance.get('is_fully_compliant') else '❌ No'}")
        
        details = compliance.get('details', {})
        if details:
            print("\n  📋 Standard-by-Standard Analysis:")
            for standard, info in details.items():
                status = "✅ Found" if info.get('found') else "❌ Missing"
                print(f"    • {standard}: {status}")
    
    # Penalties and Bonuses
    penalty = score_breakdown.get('compliance_penalty', 0)
    if penalty > 0:
        print(f"\n⚠️ Compliance Penalty: -{penalty} points")
    
    diversity_bonus = score_breakdown.get('diversity_bonus', 0)
    if diversity_bonus > 0:
        print(f"🌍 Diversity Bonus: +{diversity_bonus} points")
    
    international_bonus = score_breakdown.get('international_bonus', 0)
    if international_bonus > 0:
        print(f"🌐 International Bonus: +{international_bonus} points")
    
    # Ranking Analysis
    print(f"\n📈 RANKING ANALYSIS:")
    print("-" * 40)
    
    rankings = analyzer.calculate_organization_rankings('Mayo Clinic', mayo_info.get('total_score', 0))
    if rankings:
        print(f"🏅 Overall Rank: {rankings.get('overall_rank', 'N/A')}")
        print(f"📊 Percentile: {rankings.get('percentile', 'N/A'):.2f}%")
    
    # Why the low score?
    print(f"\n🔍 WHY MAYO CLINIC HAS LOW QuXAT SCORE:")
    print("-" * 50)
    
    reasons = []
    
    # Check JCI status
    jci_info = cert_breakdown.get('JCI', {})
    if jci_info.get('count', 0) == 0:
        reasons.append("❌ No JCI (Joint Commission International) accreditation found")
    else:
        print(f"✅ Has JCI accreditation: {jci_info.get('total_score', 0)} points")
    
    # Check NABH status
    nabh_info = cert_breakdown.get('NABH', {})
    if nabh_info.get('count', 0) == 0:
        reasons.append("❌ No NABH (National Accreditation Board for Hospitals) accreditation")
        reasons.append("   (NABH is primarily for Indian hospitals)")
    
    # Check ISO compliance
    if compliance.get('compliant_count', 0) == 0:
        reasons.append("❌ No ISO certifications found (ISO 9001, 14001, 45001, etc.)")
    
    # Check quality initiatives
    if quality_score == 0:
        reasons.append("❌ No quality initiatives detected from website")
    
    # Check patient feedback
    if feedback_score == 0:
        reasons.append("❌ No patient feedback data available")
    
    if reasons:
        print("🚨 MAIN ISSUES:")
        for i, reason in enumerate(reasons, 1):
            print(f"{i}. {reason}")
    
    # Comparison with high-scoring hospital
    print(f"\n🆚 COMPARISON WITH HIGH-SCORING HOSPITAL:")
    print("-" * 50)
    
    fortis_info = analyzer.search_organization_info("Fortis Memorial Research Institute")
    if fortis_info:
        fortis_score = fortis_info.get('total_score', 0)
        print(f"Fortis Memorial Research Institute Score: {fortis_score}")
        print(f"Mayo Clinic Score: {mayo_info.get('total_score', 0)}")
        print(f"Score Difference: {fortis_score - mayo_info.get('total_score', 0)} points")
        
        fortis_breakdown = fortis_info.get('certification_breakdown', {})
        mayo_breakdown = cert_breakdown
        
        print("\nCertification Comparison:")
        print("Hospital                    | JCI Score | NABH Score")
        print("-" * 55)
        mayo_jci = mayo_breakdown.get('JCI', {}).get('total_score', 0)
        mayo_nabh = mayo_breakdown.get('NABH', {}).get('total_score', 0)
        fortis_jci = fortis_breakdown.get('JCI', {}).get('total_score', 0)
        fortis_nabh = fortis_breakdown.get('NABH', {}).get('total_score', 0)
        
        print(f"Mayo Clinic                 | {mayo_jci:8.1f} | {mayo_nabh:9.1f}")
        print(f"Fortis Memorial RI          | {fortis_jci:8.1f} | {fortis_nabh:9.1f}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS TO IMPROVE MAYO CLINIC SCORE:")
    print("-" * 55)
    print("1. 🏆 Verify JCI accreditation status in QuXAT database")
    print("2. 📋 Add ISO certification data (9001, 14001, 45001, etc.)")
    print("3. 🌐 Include quality initiatives from Mayo Clinic website")
    print("4. 👥 Integrate patient satisfaction/feedback data")
    print("5. 🔧 Consider US-specific healthcare standards (not just Indian NABH)")
    print("6. 📊 Weight international reputation more heavily")
    
    print(f"\n🎯 CONCLUSION:")
    print("-" * 20)
    print("Mayo Clinic's low QuXAT score is primarily due to:")
    print("• QuXAT system being optimized for Indian healthcare standards (NABH)")
    print("• Missing or unrecognized international certifications")
    print("• Lack of comprehensive quality initiative data")
    print("• No patient feedback integration")
    print("• Heavy penalty for non-compliance with Indian-specific standards")

if __name__ == "__main__":
    analyze_mayo_clinic()