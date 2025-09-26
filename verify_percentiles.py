import json

# Load the scored organizations
with open('scored_organizations_complete.json', 'r') as f:
    data = json.load(f)

print("Percentile Verification Report")
print("=" * 50)

# Group organizations by score to verify percentile calculations
score_groups = {}
for org in data:
    score = org['total_score']
    if score not in score_groups:
        score_groups[score] = []
    score_groups[score].append(org)

# Sort scores in descending order
sorted_scores = sorted(score_groups.keys(), reverse=True)

print(f"Total organizations: {len(data)}")
print(f"Unique score levels: {len(sorted_scores)}")
print()

print("Score Distribution and Percentiles:")
print("-" * 70)
print(f"{'Score':<8} {'Count':<8} {'Rank':<8} {'Percentile':<12} {'Sample Organization'}")
print("-" * 70)

for score in sorted_scores:
    orgs = score_groups[score]
    sample_org = orgs[0]  # Take first organization as sample
    
    print(f"{score:<8} {len(orgs):<8} {sample_org['overall_rank']:<8} {sample_org['percentile']:<12.2f} {sample_org['name'][:30]}")

print()

# Verify percentile calculation logic
print("Percentile Calculation Verification:")
print("-" * 40)

total_orgs = len(data)
for score in sorted_scores[:3]:  # Check top 3 score groups
    orgs = score_groups[score]
    rank = orgs[0]['overall_rank']
    percentile = orgs[0]['percentile']
    
    # Calculate expected percentile: (total_orgs - rank + 1) / total_orgs * 100
    expected_percentile = ((total_orgs - rank + 1) / total_orgs) * 100
    
    print(f"Score {score}: Rank {rank}")
    print(f"  Calculated percentile: {percentile:.2f}%")
    print(f"  Expected percentile: {expected_percentile:.2f}%")
    print(f"  Match: {'✓' if abs(percentile - expected_percentile) < 0.01 else '✗'}")
    print()

# Check if all organizations have percentiles
orgs_without_percentiles = [org for org in data if 'percentile' not in org or org['percentile'] is None]
print(f"Organizations without percentiles: {len(orgs_without_percentiles)}")

if len(orgs_without_percentiles) == 0:
    print("✅ SUCCESS: All organizations have percentile scores!")
else:
    print("❌ ERROR: Some organizations are missing percentile scores")
    for org in orgs_without_percentiles[:5]:
        print(f"  - {org['name']}")

# Verify percentile range
percentiles = [org['percentile'] for org in data if 'percentile' in org and org['percentile'] is not None]
if percentiles:
    min_percentile = min(percentiles)
    max_percentile = max(percentiles)
    print(f"\nPercentile range: {min_percentile:.2f}% to {max_percentile:.2f}%")
    
    if min_percentile >= 0 and max_percentile <= 100:
        print("✅ Percentile range is valid (0-100%)")
    else:
        print("❌ Invalid percentile range detected")