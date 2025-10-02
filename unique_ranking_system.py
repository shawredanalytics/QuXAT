"""
Unique Ranking System for QuXAT Healthcare Quality Grid
This module ensures every healthcare organization receives a unique rank
based on the QuXAT scoring methodology with proper tie-breaking.
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple
import logging

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UniqueRankingSystem:
    """System to ensure unique rankings for all healthcare organizations"""
    
    def __init__(self):
        """Initialize the unique ranking system"""
        self.organizations = []
        self.ranking_results = {}
        
    def load_scored_organizations(self, filename: str = 'scored_organizations_complete.json') -> bool:
        """Load scored organizations from file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    self.organizations = json.load(f)
                logger.info(f"Loaded {len(self.organizations)} organizations from {filename}")
                # Apply organization-specific filtering to exclude group-level entries
                try:
                    all_names = [o.get('name', '') for o in self.organizations]
                    self.organizations = [
                        o for o in self.organizations
                        if not self._is_group_level(o.get('name', ''), all_names)
                    ]
                    logger.info(f"Filtered to {len(self.organizations)} organization-specific entries (removed group-level)")
                except Exception as e:
                    logger.warning(f"Filtering group-level entries failed: {e}")
                return True
            else:
                logger.error(f"File {filename} not found")
                return False
        except Exception as e:
            logger.error(f"Error loading organizations: {e}")
            return False
    
    def apply_unique_ranking(self) -> List[Dict]:
        """Apply unique ranking with tie-breaking to all organizations"""
        logger.info("Applying unique ranking with tie-breaking...")
        
        if not self.organizations:
            logger.error("No organizations loaded")
            return []
        
        # Sort organizations with multiple criteria for unique ranking:
        # 1. Total score (descending) - primary criterion
        # 2. Certification count (descending) - first tie-breaker  
        # 3. Organization name (ascending) - final tie-breaker for complete uniqueness
        sorted_orgs = sorted(
            self.organizations,
            key=lambda x: (
                -x.get('total_score', 0),  # Negative for descending order
                -x.get('certification_count', 0),  # Negative for descending order
                x.get('name', '').lower()  # Ascending alphabetical order
            )
        )
        
        # Assign unique sequential ranks
        for i, org in enumerate(sorted_orgs):
            # Each organization gets a unique rank from 1 to N
            unique_rank = i + 1
            
            # Store original rank for comparison
            original_rank = org.get('overall_rank', 0)
            
            # Assign new unique rank and calculate percentile
            org['overall_rank'] = unique_rank
            org['percentile'] = ((len(sorted_orgs) - unique_rank + 1) / len(sorted_orgs)) * 100
            
            # Add ranking metadata for transparency
            org['ranking_metadata'] = {
                'original_rank': original_rank,
                'unique_rank': unique_rank,
                'tie_breaking_criteria': {
                    'primary_score': org.get('total_score', 0),
                    'certification_count': org.get('certification_count', 0),
                    'alphabetical_name': org.get('name', '')
                },
                'ranking_timestamp': datetime.now().isoformat()
            }
        
        self.organizations = sorted_orgs
        logger.info(f"Applied unique ranking to {len(sorted_orgs)} organizations")
        
        return sorted_orgs
    
    def validate_unique_rankings(self) -> Dict[str, any]:
        """Validate that all rankings are unique"""
        logger.info("Validating unique rankings...")
        
        ranks = [org.get('overall_rank', 0) for org in self.organizations]
        unique_ranks = set(ranks)
        
        validation_results = {
            'total_organizations': len(self.organizations),
            'total_ranks': len(ranks),
            'unique_ranks': len(unique_ranks),
            'is_unique': len(ranks) == len(unique_ranks),
            'duplicate_ranks': [],
            'rank_gaps': [],
            'expected_rank_range': (1, len(self.organizations))
        }
        
        # Check for duplicates
        if not validation_results['is_unique']:
            rank_counts = {}
            for rank in ranks:
                rank_counts[rank] = rank_counts.get(rank, 0) + 1
            
            validation_results['duplicate_ranks'] = [
                {'rank': rank, 'count': count} 
                for rank, count in rank_counts.items() 
                if count > 1
            ]
        
        # Check for gaps in ranking sequence
        expected_ranks = set(range(1, len(self.organizations) + 1))
        actual_ranks = set(ranks)
        missing_ranks = expected_ranks - actual_ranks
        extra_ranks = actual_ranks - expected_ranks
        
        if missing_ranks or extra_ranks:
            validation_results['rank_gaps'] = {
                'missing_ranks': sorted(list(missing_ranks)),
                'extra_ranks': sorted(list(extra_ranks))
            }
        
        # Log validation results
        if validation_results['is_unique'] and not missing_ranks and not extra_ranks:
            logger.info("✅ All rankings are unique and sequential!")
        else:
            logger.warning("❌ Ranking validation failed!")
            if validation_results['duplicate_ranks']:
                logger.warning(f"Duplicate ranks found: {validation_results['duplicate_ranks']}")
            if missing_ranks:
                logger.warning(f"Missing ranks: {sorted(list(missing_ranks))}")
            if extra_ranks:
                logger.warning(f"Extra ranks: {sorted(list(extra_ranks))}")
        
        return validation_results
    
    def generate_ranking_statistics(self) -> Dict:
        """Generate comprehensive statistics for the unique ranking system"""
        logger.info("Generating ranking statistics...")
        
        scores = [org.get('total_score', 0) for org in self.organizations]
        
        stats = {
            'ranking_system_info': {
                'system_type': 'Unique Sequential Ranking',
                'tie_breaking_criteria': [
                    'Total QuXAT Score (Primary)',
                    'Certification Count (Secondary)', 
                    'Organization Name Alphabetical (Tertiary)'
                ],
                'generation_timestamp': datetime.now().isoformat()
            },
            'organization_statistics': {
                'total_organizations': len(self.organizations),
                'unique_ranks_assigned': len(set(org.get('overall_rank', 0) for org in self.organizations)),
                'rank_range': (1, len(self.organizations))
            },
            'score_statistics': {
                'average_score': sum(scores) / len(scores) if scores else 0,
                'median_score': sorted(scores)[len(scores)//2] if scores else 0,
                'highest_score': max(scores) if scores else 0,
                'lowest_score': min(scores) if scores else 0,
                'score_distribution': {
                    'A+ (75-100)': len([s for s in scores if s >= 75]),
                    'A (65-74)': len([s for s in scores if 65 <= s < 75]),
                    'B+ (55-64)': len([s for s in scores if 55 <= s < 65]),
                    'B (45-54)': len([s for s in scores if 45 <= s < 55]),
                    'C (0-44)': len([s for s in scores if s < 45])
                }
            },
            'top_10_organizations': [
                {
                    'rank': org.get('overall_rank', 0),
                    'name': org.get('name', ''),
                    'country': org.get('country', ''),
                    'total_score': org.get('total_score', 0),
                    'certification_count': org.get('certification_count', 0),
                    'percentile': org.get('percentile', 0)
                }
                for org in self.organizations[:10]
            ]
        }
        
        self.ranking_results = stats
        return stats
    
    def save_unique_rankings(self, output_prefix: str = 'unique_rankings') -> Dict[str, str]:
        """Save the unique rankings to files"""
        logger.info("Saving unique rankings...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        files_created = {}
        
        # Save complete ranked organizations
        organizations_file = f'{output_prefix}_complete_{timestamp}.json'
        with open(organizations_file, 'w', encoding='utf-8') as f:
            json.dump(self.organizations, f, indent=2, ensure_ascii=False)
        files_created['organizations'] = organizations_file
        
        # Save ranking statistics
        stats_file = f'{output_prefix}_statistics_{timestamp}.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.ranking_results, f, indent=2, ensure_ascii=False)
        files_created['statistics'] = stats_file
        
        # Save validation results
        validation_results = self.validate_unique_rankings()
        validation_file = f'{output_prefix}_validation_{timestamp}.json'
        with open(validation_file, 'w', encoding='utf-8') as f:
            json.dump(validation_results, f, indent=2, ensure_ascii=False)
        files_created['validation'] = validation_file
        
        # Save CSV for easy viewing
        csv_file = f'{output_prefix}_summary_{timestamp}.csv'
        with open(csv_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write('rank,name,country,region,hospital_type,total_score,percentile,certification_count\n')
            
            # Write data
            for org in self.organizations:
                f.write(f"{org.get('overall_rank', 0)},{org.get('name', '').replace(',', ';')},"
                       f"{org.get('country', '')},{org.get('region', '')},"
                       f"{org.get('hospital_type', '')},{org.get('total_score', 0)},"
                       f"{org.get('percentile', 0):.2f},{org.get('certification_count', 0)}\n")
        files_created['csv'] = csv_file
        
        logger.info(f"Saved unique rankings to {len(files_created)} files")
        return files_created

    # --- Helper methods ---
    def _is_group_level(self, org_name: str, all_names: list) -> bool:
        """Heuristic to detect group-level entries that lack a location qualifier.
        Mirrors the logic in comprehensive_ranking_report to keep outputs consistent.
        """
        if not org_name:
            return False
        name = org_name.strip()
        # Explicit group/network keywords
        group_indicators = ['Group', 'Network', 'Hospital Group', 'Health System', 'Private Hospital Network']
        for kw in group_indicators:
            if kw.lower() in name.lower():
                return True
        # Location qualifier
        if ',' in name or ('(' in name and ')' in name):
            return False
        # Prefix variant check
        for other in all_names:
            if other == name:
                continue
            low = other.strip()
            if low.startswith(name + ' ') or low.startswith(name + ','):
                return True
        return False
    
    def run_complete_unique_ranking(self) -> bool:
        """Run the complete unique ranking process"""
        logger.info("Starting complete unique ranking process...")
        
        try:
            # Step 1: Load organizations
            if not self.load_scored_organizations():
                logger.error("Failed to load organizations")
                return False
            
            # Step 2: Apply unique ranking
            ranked_orgs = self.apply_unique_ranking()
            if not ranked_orgs:
                logger.error("Failed to apply unique ranking")
                return False
            
            # Step 3: Validate rankings
            validation_results = self.validate_unique_rankings()
            if not validation_results['is_unique']:
                logger.error("Ranking validation failed")
                return False
            
            # Step 4: Generate statistics
            self.generate_ranking_statistics()
            
            # Step 5: Save results
            files_created = self.save_unique_rankings()
            
            # Print summary
            print(f"\n{'='*70}")
            print("UNIQUE RANKING SYSTEM - PROCESS COMPLETED")
            print(f"{'='*70}")
            print(f"✅ Total Organizations Ranked: {len(self.organizations):,}")
            print(f"✅ All Rankings Are Unique: {validation_results['is_unique']}")
            print(f"✅ Rank Range: {validation_results['expected_rank_range'][0]} to {validation_results['expected_rank_range'][1]}")
            print(f"\n📊 Score Distribution:")
            for grade, count in self.ranking_results['score_statistics']['score_distribution'].items():
                print(f"   {grade}: {count:,} organizations")
            
            print(f"\n🏆 Top 5 Organizations:")
            for i, org in enumerate(self.organizations[:5]):
                print(f"   {org['overall_rank']}. {org['name']} ({org['country']}) - Score: {org['total_score']:.1f}")
            
            print(f"\n📁 Files Generated:")
            for file_type, filename in files_created.items():
                print(f"   {file_type.title()}: {filename}")
            
            logger.info("Unique ranking process completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error in unique ranking process: {e}")
            return False

if __name__ == "__main__":
    ranking_system = UniqueRankingSystem()
    success = ranking_system.run_complete_unique_ranking()
    
    if success:
        print("\n🎉 Unique ranking system completed successfully!")
    else:
        print("\n❌ Unique ranking system failed. Check logs for details.")