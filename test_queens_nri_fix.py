#!/usr/bin/env python3
"""
Test script to verify that Queens NRI Hospital no longer shows JCI accreditation
after the data correction.
"""

import json
import sys
from pathlib import Path

def test_queens_nri_jci_fix():
    """Test that Queens NRI Hospital no longer has JCI accreditation in the data files."""
    
    print("Testing Queens NRI Hospital JCI accreditation fix...")
    print("=" * 60)
    
    # Files to check
    files_to_check = [
        "unified_healthcare_organizations.json",
        "ranking_statistics.json", 
        "scored_organizations_complete.json"
    ]
    
    all_tests_passed = True
    
    for filename in files_to_check:
        filepath = Path(filename)
        if not filepath.exists():
            print(f"❌ File not found: {filename}")
            all_tests_passed = False
            continue
            
        print(f"\n📁 Checking {filename}...")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Find Queens NRI Hospital entry
            queens_nri_entry = None
            
            if isinstance(data, list):
                for entry in data:
                    if "Queens NRI Hospital" in entry.get("name", ""):
                        queens_nri_entry = entry
                        break
            elif isinstance(data, dict):
                # For ranking_statistics.json which has a different structure
                # Check if it's a single organization entry
                if "Queens NRI Hospital" in data.get("name", ""):
                    queens_nri_entry = data
                else:
                    # Look for Queens NRI Hospital in nested structures
                    for key, value in data.items():
                        if isinstance(value, dict) and "Queens NRI Hospital" in value.get("name", ""):
                            queens_nri_entry = value
                            break
                        elif isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict) and "Queens NRI Hospital" in item.get("name", ""):
                                    queens_nri_entry = item
                                    break
            
            if not queens_nri_entry:
                print(f"   ⚠️  Queens NRI Hospital not found in {filename}")
                continue
                
            # Check certifications
            certifications = queens_nri_entry.get("certifications", [])
            jci_found = False
            nabh_found = False
            
            for cert in certifications:
                cert_name = cert.get("name", "").lower()
                if "jci" in cert_name or "joint commission" in cert_name:
                    jci_found = True
                    print(f"   ❌ JCI certification still found: {cert.get('name')}")
                elif "nabh" in cert_name:
                    nabh_found = True
                    print(f"   ✅ NABH certification found: {cert.get('name')}")
            
            if not jci_found:
                print(f"   ✅ No JCI certification found")
            else:
                all_tests_passed = False
                
            if nabh_found:
                print(f"   ✅ NABH certification preserved")
            else:
                print(f"   ⚠️  NABH certification not found")
            
            # Check quality indicators if present
            quality_indicators = queens_nri_entry.get("quality_indicators", {})
            if quality_indicators:
                jci_accredited = quality_indicators.get("jci_accredited", None)
                if jci_accredited is False:
                    print(f"   ✅ Quality indicators correctly show jci_accredited: false")
                elif jci_accredited is True:
                    print(f"   ❌ Quality indicators incorrectly show jci_accredited: true")
                    all_tests_passed = False
                else:
                    print(f"   ⚠️  jci_accredited field not found in quality indicators")
            
            # Check scores
            total_score = queens_nri_entry.get("total_score", 0)
            certification_score = queens_nri_entry.get("certification_score", 0)
            
            if total_score == 18 and certification_score == 18:
                print(f"   ✅ Scores correctly updated: total={total_score}, certification={certification_score}")
            else:
                print(f"   ❌ Scores incorrect: total={total_score}, certification={certification_score} (expected 18, 18)")
                all_tests_passed = False
                
        except Exception as e:
            print(f"   ❌ Error reading {filename}: {e}")
            all_tests_passed = False
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("✅ ALL TESTS PASSED: Queens NRI Hospital JCI accreditation successfully removed!")
        return True
    else:
        print("❌ SOME TESTS FAILED: Issues found with Queens NRI Hospital data correction")
        return False

if __name__ == "__main__":
    success = test_queens_nri_jci_fix()
    sys.exit(0 if success else 1)