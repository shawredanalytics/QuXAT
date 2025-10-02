#!/usr/bin/env python3
"""
Test script for Mandatory Accreditation Requirements
Tests the updated scoring methodology with JCI, ISO 9001, ISO 15189, and Magnet Recognition as mandatory requirements.
"""

import json
from international_scoring_algorithm import InternationalHealthcareScorer
from public_domain_fallback_system import PublicDomainFallbackSystem

def test_mandatory_accreditations():
    """Test the mandatory accreditation requirements in the scoring system."""
    
    print("🧪 Testing Mandatory Accreditation Requirements")
    print("=" * 60)
    
    # Initialize the scoring algorithm
    scoring_algorithm = InternationalHealthcareScorer()
    
    # Test Case 1: Organization with all mandatory accreditations
    print("\n1. Testing organization WITH all mandatory accreditations:")
    print("-" * 50)
    
    compliant_org = {
        "name": "Test Hospital - Fully Compliant",
        "certifications": [
            {
                "type": "CAP",
                "standard": "CAP 15189",
                "status": "Active",
                "valid_until": "2025-12-31",
                "issuer": "College of American Pathologists"
            },
            {
                "type": "JCI",
                "standard": "JCI Hospital Standards",
                "status": "Active", 
                "valid_until": "2025-12-31",
                "issuer": "Joint Commission International"
            },
            {
                "type": "ISO",
                "standard": "ISO 9001",
                "status": "Active",
                "valid_until": "2025-12-31",
                "issuer": "ISO Certification Body"
            },
            {
                "type": "ISO",
                "standard": "ISO 15189",
                "status": "Active",
                "valid_until": "2025-12-31",
                "issuer": "ISO Certification Body"
            },
            {
                "type": "Magnet",
                "name": "Magnet Recognition Program",
                "status": "Active",
                "valid_until": "2025-12-31",
                "issuer": "ANCC"
            }
        ]
    }
    
    result_compliant = scoring_algorithm.calculate_international_quality_score(compliant_org["certifications"])
    print(f"✅ Total Score: {result_compliant['total_score']:.2f}/100")
    print(f"📊 Certification Score: {result_compliant['certification_score']:.2f}")
    print(f"🎯 Mandatory Compliance: {result_compliant.get('mandatory_compliance', {})}")
    print(f"⚠️ Mandatory Penalties: {result_compliant.get('total_penalty', 0)}")
    
    # Test Case 2: Organization missing some mandatory accreditations
    print("\n2. Testing organization MISSING some mandatory accreditations:")
    print("-" * 50)
    
    partial_org = {
        "name": "Test Hospital - Partially Compliant",
        "certifications": [
            {
                "type": "CAP",
                "standard": "CAP 15189",
                "status": "Active",
                "valid_until": "2025-12-31",
                "issuer": "College of American Pathologists"
            },
            {
                "type": "ISO",
                "standard": "ISO 9001",
                "status": "Active",
                "valid_until": "2025-12-31",
                "issuer": "ISO Certification Body"
            }
            # Missing JCI and Magnet
        ]
    }
    
    result_partial = scoring_algorithm.calculate_international_quality_score(partial_org["certifications"])
    print(f"⚠️ Total Score: {result_partial['total_score']:.2f}/100")
    print(f"📊 Certification Score: {result_partial['certification_score']:.2f}")
    print(f"🎯 Mandatory Compliance: {result_partial.get('mandatory_compliance', {})}")
    # Calculate total mandatory penalties from algorithm output
    partial_penalties_total = sum(result_partial.get('mandatory_penalties', {}).values())
    print(f"⚠️ Mandatory Penalties: {partial_penalties_total}")
    
    # Test Case 3: Organization with NO mandatory accreditations
    print("\n3. Testing organization with NO mandatory accreditations:")
    print("-" * 50)
    
    non_compliant_org = {
        "name": "Test Hospital - Non-Compliant",
        "certifications": [
            {
                "type": "NABH",
                "standard": "NABH Hospital Standards",
                "status": "Active",
                "valid_until": "2025-12-31",
                "issuer": "National Accreditation Board"
            }
            # Missing all mandatory accreditations
        ]
    }
    
    result_non_compliant = scoring_algorithm.calculate_international_quality_score(non_compliant_org["certifications"])
    print(f"❌ Total Score: {result_non_compliant['total_score']:.2f}/100")
    print(f"📊 Certification Score: {result_non_compliant['certification_score']:.2f}")
    print(f"🎯 Mandatory Compliance: {result_non_compliant.get('mandatory_compliance', {})}")
    non_compliant_penalties_total = sum(result_non_compliant.get('mandatory_penalties', {}).values())
    print(f"⚠️ Mandatory Penalties: {non_compliant_penalties_total}")
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print(f"✅ Fully Compliant Score: {result_compliant['total_score']:.2f}")
    print(f"⚠️ Partially Compliant Score: {result_partial['total_score']:.2f}")
    print(f"❌ Non-Compliant Score: {result_non_compliant['total_score']:.2f}")
    
    # Verify penalties are being applied (compute dynamically from algorithm configuration)
    mandatory_config = scoring_algorithm.mandatory_accreditations
    expected_partial_missing = ['JCI', 'MAGNET_RECOGNITION']
    expected_penalty_partial = sum(mandatory_config[k]['penalty'] for k in expected_partial_missing)
    expected_full_penalty = sum(info['penalty'] for info in mandatory_config.values())

    print(f"\n🔍 Penalty Verification:")
    print(f"Expected partial penalty: {expected_penalty_partial}")
    print(f"Actual partial penalty: {partial_penalties_total}")
    print(f"Expected full penalty: {expected_full_penalty}")
    print(f"Actual full penalty: {non_compliant_penalties_total}")

def test_fallback_system_mandatory():
    """Test the fallback system with mandatory accreditations."""
    
    print("\n\n🔄 Testing Public Domain Fallback System")
    print("=" * 60)
    
    fallback_system = PublicDomainFallbackSystem()
    
    # Test with an organization that would have no accreditations
    result = fallback_system.generate_fallback_organization_data("Test Unknown Hospital")
    
    if result:
        print(f"🏥 Organization: Test Unknown Hospital")
        print(f"📊 Total Score: {result.get('total_score', 0):.2f}/100")
        print(f"⚠️ Mandatory Penalties: {result.get('mandatory_penalties', 0)}")
        print(f"🎯 Mandatory Compliance: {result.get('mandatory_compliance', {})}")
        
        if 'mandatory_warning' in result:
            print(f"⚠️ Warning: {result['mandatory_warning']}")
    else:
        print("❌ Failed to generate fallback data")

if __name__ == "__main__":
    test_mandatory_accreditations()
    test_fallback_system_mandatory()
    print("\n🎉 Mandatory Accreditation Testing Complete!")