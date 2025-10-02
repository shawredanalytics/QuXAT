#!/usr/bin/env python3
"""
Improve Search Logic for QuXAT Scoring System

This script enhances the organization search functionality to handle:
1. Typos and misspellings (e.g., "john hopkins" -> "Johns Hopkins")
2. Partial matches with better fuzzy matching
3. Word order variations
4. Common abbreviations and variations

Author: QuXAT Development Team
Date: 2025-01-28
"""

import json
import re
from difflib import SequenceMatcher
from typing import List, Dict, Optional, Tuple

def load_unified_database():
    """Load the unified healthcare database"""
    try:
        with open('unified_healthcare_organizations_with_nabl.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Unified database not found")
        return []

def similarity_score(a: str, b: str) -> float:
    """Calculate similarity score between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def word_overlap_score(search_words: List[str], target_words: List[str]) -> float:
    """Calculate word overlap score between search terms and target"""
    search_set = set(word.lower() for word in search_words)
    target_set = set(word.lower() for word in target_words)
    
    if not search_set or not target_set:
        return 0.0
    
    intersection = search_set.intersection(target_set)
    return len(intersection) / len(search_set)

def normalize_organization_name(name: str) -> str:
    """Normalize organization name for better matching"""
    # Remove common suffixes and prefixes
    name = re.sub(r'\b(hospital|medical|center|centre|institute|research|health|care|system|ltd|limited|pvt|private|inc|corporation|corp)\b', '', name, flags=re.IGNORECASE)
    
    # Remove special characters and extra spaces
    name = re.sub(r'[^\w\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name

def enhanced_search(search_term: str, database: List[Dict], threshold: float = 0.6) -> List[Tuple[Dict, float]]:
    """
    Enhanced search with fuzzy matching and typo tolerance
    
    Args:
        search_term: User's search input
        database: List of organization dictionaries
        threshold: Minimum similarity score to include in results
    
    Returns:
        List of (organization, score) tuples sorted by relevance
    """
    if not search_term or not database:
        return []
    
    search_term = search_term.strip()
    search_words = search_term.lower().split()
    normalized_search = normalize_organization_name(search_term)
    
    results = []
    
    for org in database:
        if not isinstance(org, dict):
            continue
            
        org_name = org.get('name', '')
        original_name = org.get('original_name', '')
        
        if not org_name:
            continue
        
        # Calculate multiple similarity scores
        scores = []
        
        # 1. Direct similarity with organization name
        direct_score = similarity_score(search_term, org_name)
        scores.append(('direct', direct_score))
        
        # 2. Normalized name similarity
        normalized_org = normalize_organization_name(org_name)
        normalized_score = similarity_score(normalized_search, normalized_org)
        scores.append(('normalized', normalized_score))
        
        # 3. Word overlap score
        org_words = org_name.lower().split()
        overlap_score = word_overlap_score(search_words, org_words)
        scores.append(('overlap', overlap_score))
        
        # 4. Substring matching (original logic)
        search_lower = search_term.lower()
        org_lower = org_name.lower()
        if search_lower in org_lower or org_lower in search_lower:
            scores.append(('substring', 1.0))
        else:
            scores.append(('substring', 0.0))
        
        # 5. Original name matching (if available)
        if original_name:
            original_score = similarity_score(search_term, original_name)
            scores.append(('original', original_score))
            
            original_lower = original_name.lower()
            if search_lower in original_lower or original_lower in search_lower:
                scores.append(('original_substring', 1.0))
            else:
                scores.append(('original_substring', 0.0))
        
        # Calculate weighted final score
        weights = {
            'direct': 0.3,
            'normalized': 0.25,
            'overlap': 0.2,
            'substring': 0.15,
            'original': 0.05,
            'original_substring': 0.05
        }
        
        final_score = sum(score * weights.get(score_type, 0) for score_type, score in scores)
        
        # Boost score for exact matches
        if org_name.lower() == search_term.lower():
            final_score = 1.0
        elif search_term.lower() in org_name.lower():
            final_score = max(final_score, 0.9)
        
        if final_score >= threshold:
            results.append((org, final_score))
    
    # Sort by score (descending)
    results.sort(key=lambda x: x[1], reverse=True)
    return results

def test_search_improvements():
    """Test the improved search functionality"""
    print("🔍 Testing Enhanced Search Logic for QuXAT Scoring System")
    print("=" * 60)
    
    # Load database
    database = load_unified_database()
    if not database:
        print("❌ Could not load database for testing")
        return
    
    print(f"📊 Loaded {len(database)} organizations from unified database")
    
    # Test cases
    test_cases = [
        "john hopkins",           # Missing 's' - should find Johns Hopkins
        "johns hopkins",          # Correct spelling
        "Johns Hopkins Hospital", # Full name
        "JOHNS HOPKINS",          # All caps
        "mayo clinic",            # Should find Mayo Clinic
        "fortis memorial",        # Partial name
        "apollo hospital",        # Common name
        "max healthcare",         # Another common name
    ]
    
    print("\n🧪 Testing Search Cases:")
    print("-" * 40)
    
    for search_term in test_cases:
        print(f"\n🔍 Searching for: '{search_term}'")
        results = enhanced_search(search_term, database, threshold=0.4)
        
        if results:
            print(f"✅ Found {len(results)} matches:")
            for i, (org, score) in enumerate(results[:3]):  # Show top 3
                org_name = org.get('name', 'Unknown')
                certifications = len(org.get('certifications', []))
                print(f"   {i+1}. {org_name} (Score: {score:.3f}, Certs: {certifications})")
        else:
            print("❌ No matches found")
    
    # Specific test for Johns Hopkins issue
    print("\n" + "=" * 60)
    print("🎯 Specific Test: 'john hopkins' -> 'Johns Hopkins Hospital'")
    print("-" * 60)
    
    results = enhanced_search("john hopkins", database, threshold=0.3)
    johns_hopkins_found = False
    
    for org, score in results:
        org_name = org.get('name', '')
        if 'johns hopkins' in org_name.lower():
            johns_hopkins_found = True
            certifications = org.get('certifications', [])
            quality_score = org.get('quality_score', 'N/A')
            
            print(f"✅ FOUND: {org_name}")
            print(f"   📊 Match Score: {score:.3f}")
            print(f"   🏆 Certifications: {len(certifications)}")
            print(f"   ⭐ Quality Score: {quality_score}")
            
            if certifications:
                print(f"   🔖 Certification Types:")
                for cert in certifications[:3]:  # Show first 3
                    cert_type = cert.get('type', 'Unknown')
                    print(f"      - {cert_type}")
            break
    
    if not johns_hopkins_found:
        print("❌ Johns Hopkins Hospital not found with 'john hopkins' search")
        
        # Check if it exists in database at all
        for org in database:
            org_name = org.get('name', '')
            if 'johns hopkins' in org_name.lower():
                print(f"🔍 Found in database: {org_name}")
                break
    
    print("\n" + "=" * 60)
    print("📋 Recommendations:")
    print("1. Implement enhanced search in Streamlit app")
    print("2. Use fuzzy matching with configurable threshold")
    print("3. Consider word order variations")
    print("4. Handle common typos and abbreviations")
    print("5. Provide search suggestions for partial matches")

if __name__ == "__main__":
    test_search_improvements()