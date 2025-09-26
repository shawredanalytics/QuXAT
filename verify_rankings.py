import json

# Load the scored organizations
with open('scored_organizations_complete.json', 'r') as f:
    data = json.load(f)

# Find organizations with score 70
top_orgs = [org for org in data if org['total_score'] == 70]

print(f"Organizations with score 70.0:")
print(f"Total count: {len(top_orgs)}")
print()

for i, org in enumerate(top_orgs[:10]):
    print(f"Rank {org['overall_rank']}: {org['name']} - Score: {org['total_score']}")

print()

# Check if all organizations with the same score have the same rank
score_groups = {}
for org in data:
    score = org['total_score']
    if score not in score_groups:
        score_groups[score] = []
    score_groups[score].append(org)

print("Verifying tie handling:")
tie_issues = 0
for score, orgs in score_groups.items():
    if len(orgs) > 1:  # Multiple organizations with same score
        ranks = set(org['overall_rank'] for org in orgs)
        if len(ranks) > 1:
            print(f"ERROR: Score {score} has organizations with different ranks: {ranks}")
            tie_issues += 1
        else:
            print(f"✓ Score {score}: {len(orgs)} organizations all have rank {list(ranks)[0]}")

if tie_issues == 0:
    print(f"\n✅ SUCCESS: All organizations with identical scores have identical ranks!")
else:
    print(f"\n❌ ISSUES FOUND: {tie_issues} score groups have inconsistent rankings")

# Show some statistics
print(f"\nRanking Statistics:")
print(f"Total organizations: {len(data)}")
print(f"Unique scores: {len(score_groups)}")
print(f"Score groups with ties: {sum(1 for orgs in score_groups.values() if len(orgs) > 1)}")