#!/usr/bin/env python3
"""
Test script to demonstrate the ranking bug
"""

def current_ranking_logic(all_orgs, current_score):
    """Current buggy ranking logic"""
    # Sort organizations by total score (descending)
    all_orgs.sort(key=lambda x: x['total_score'], reverse=True)
    
    # Find ranking position with current logic
    rank = 1
    organizations_with_higher_scores = 0
    
    for org in all_orgs:
        if org['total_score'] > current_score:
            organizations_with_higher_scores += 1
        else:
            break  # Since list is sorted in descending order
    
    rank = organizations_with_higher_scores + 1
    return rank

def correct_ranking_logic(all_orgs, current_score, current_org_name):
    """Correct ranking logic"""
    # Add current organization to the list
    all_orgs_with_current = all_orgs + [{'name': current_org_name, 'total_score': current_score}]
    
    # Sort organizations by total score (descending)
    all_orgs_with_current.sort(key=lambda x: x['total_score'], reverse=True)
    
    # Find the position of current organization
    for i, org in enumerate(all_orgs_with_current):
        if org['name'] == current_org_name:
            return i + 1  # Rank is position + 1 (1-indexed)
    
    return None

# Test data simulating the issue
test_orgs = [
    {'name': 'Org A', 'total_score': 90.0},
    {'name': 'Org B', 'total_score': 80.0},
    {'name': 'Org C', 'total_score': 70.0},
    {'name': 'Org D', 'total_score': 60.0}
]

print("=== RANKING BUG DEMONSTRATION ===")
print("Test organizations (sorted by score):")
for org in sorted(test_orgs, key=lambda x: x['total_score'], reverse=True):
    print(f"  {org['name']}: {org['total_score']}")

print("\n=== TESTING APOLLO HOSPITALS CHENNAI (Score: 88.75) ===")
apollo_score = 88.75
apollo_rank_current = current_ranking_logic(test_orgs.copy(), apollo_score)
apollo_rank_correct = correct_ranking_logic(test_orgs.copy(), apollo_score, "Apollo Hospitals Chennai")

print(f"Current (buggy) logic rank: {apollo_rank_current}")
print(f"Correct logic rank: {apollo_rank_correct}")

print("\n=== TESTING MAYO CLINIC HOSPITAL (Score: 74.0) ===")
mayo_score = 74.0
mayo_rank_current = current_ranking_logic(test_orgs.copy(), mayo_score)
mayo_rank_correct = correct_ranking_logic(test_orgs.copy(), mayo_score, "Mayo Clinic Hospital")

print(f"Current (buggy) logic rank: {mayo_rank_current}")
print(f"Correct logic rank: {mayo_rank_correct}")

print("\n=== ANALYSIS ===")
print("The current logic only counts organizations with HIGHER scores,")
print("but doesn't properly position the current organization in the sorted list.")
print("This causes multiple organizations to get the same rank when they shouldn't.")