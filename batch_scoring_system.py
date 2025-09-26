"""
Batch Scoring System for QuXAT Healthcare Quality Grid
This module processes all healthcare organizations in the database and assigns
unique ranks and percentile scores based on the QuXAT scoring logic.
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple
import logging

# Add the current directory to the path to import streamlit_app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BatchScoringSystem:
    """Batch scoring system for all healthcare organizations"""
    
    def __init__(self):
        """Initialize the batch scoring system"""
        # Import the analyzer from streamlit_app
        from streamlit_app import HealthcareOrgAnalyzer
        self.analyzer = HealthcareOrgAnalyzer()
        
        # Load the unified database
        self.load_database()
        
        # Results storage
        self.scored_organizations = []
        self.ranking_results = {}
        
    def load_database(self):
        """Load the unified healthcare organizations database"""
        try:
            with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
                self.organizations = json.load(f)
            logger.info(f"Loaded {len(self.organizations)} organizations from database")
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            raise
    
    def calculate_organization_score(self, org_data: Dict) -> Dict:
        """Calculate QuXAT score for a single organization"""
        try:
            org_name = org_data['name']
            
            # Extract certifications from the organization data
            certifications = []
            for cert in org_data.get('certifications', []):
                # Convert to the format expected by the analyzer
                cert_formatted = {
                    'name': cert.get('name', ''),
                    'type': cert.get('type', ''),
                    'status': cert.get('status', 'Active'),
                    'score_impact': cert.get('score_impact', 0),
                    'issuer': cert.get('name', ''),
                    'accreditation_date': cert.get('accreditation_date', ''),
                    'expiry_date': cert.get('expiry_date', ''),
                    'remarks': cert.get('remarks', '')
                }
                certifications.append(cert_formatted)
            
            # For now, we'll use empty quality initiatives as they're not in the database
            # In a real implementation, you might want to scrape or add this data
            quality_initiatives = []
            
            # Calculate the quality score using the analyzer's method
            score_breakdown = self.analyzer.calculate_quality_score(
                certifications=certifications,
                initiatives=quality_initiatives,
                org_name=org_name
            )
            
            # Create comprehensive organization result
            org_result = {
                'name': org_name,
                'country': org_data.get('country', 'Unknown'),
                'region': org_data.get('region', 'Unknown'),
                'hospital_type': org_data.get('hospital_type', 'Unknown'),
                'certifications': certifications,
                'certification_count': len([c for c in certifications if c['status'] == 'Active']),
                'total_score': score_breakdown['total_score'],
                'certification_score': score_breakdown['certification_score'],
                'quality_initiatives_score': score_breakdown['quality_initiatives_score'],
                'patient_feedback_score': score_breakdown.get('patient_feedback_score', 0),
                'score_breakdown': score_breakdown,
                'last_updated': datetime.now().isoformat()
            }
            
            return org_result
            
        except Exception as e:
            logger.error(f"Error calculating score for {org_data.get('name', 'Unknown')}: {e}")
            # Return a default result with zero score
            return {
                'name': org_data.get('name', 'Unknown'),
                'country': org_data.get('country', 'Unknown'),
                'region': org_data.get('region', 'Unknown'),
                'hospital_type': org_data.get('hospital_type', 'Unknown'),
                'certifications': [],
                'certification_count': 0,
                'total_score': 0,
                'certification_score': 0,
                'quality_initiatives_score': 0,
                'patient_feedback_score': 0,
                'score_breakdown': {'total_score': 0, 'certification_score': 0, 'quality_initiatives_score': 0},
                'last_updated': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def process_all_organizations(self):
        """Process and score all organizations in the database"""
        logger.info("Starting batch scoring process...")
        
        total_orgs = len(self.organizations)
        processed = 0
        
        for i, org_data in enumerate(self.organizations):
            try:
                # Calculate score for this organization
                org_result = self.calculate_organization_score(org_data)
                self.scored_organizations.append(org_result)
                
                processed += 1
                
                # Log progress every 100 organizations
                if processed % 100 == 0:
                    logger.info(f"Processed {processed}/{total_orgs} organizations ({processed/total_orgs*100:.1f}%)")
                    
            except Exception as e:
                logger.error(f"Failed to process organization {i}: {e}")
                continue
        
        logger.info(f"Completed scoring for {processed} organizations")
    
    def calculate_unique_rankings(self):
        """Calculate unique rankings for all organizations with tie-breaking"""
        logger.info("Calculating unique rankings with tie-breaking...")
        
        # Sort organizations with multiple criteria for unique ranking:
        # 1. Total score (descending) - primary criterion
        # 2. Certification count (descending) - first tie-breaker
        # 3. Organization name (ascending) - final tie-breaker for complete uniqueness
        sorted_orgs = sorted(
            self.scored_organizations, 
            key=lambda x: (
                -x['total_score'],  # Negative for descending order
                -x.get('certification_count', 0),  # Negative for descending order
                x['name'].lower()  # Ascending alphabetical order
            )
        )
        
        # Assign unique sequential ranks
        for i, org in enumerate(sorted_orgs):
            # Each organization gets a unique rank from 1 to N
            unique_rank = i + 1
            
            # Assign rank and calculate percentile based on unique position
            org['overall_rank'] = unique_rank
            org['percentile'] = ((len(sorted_orgs) - unique_rank + 1) / len(sorted_orgs)) * 100
            
            # Add tie-breaking information for transparency
            org['tie_breaking_info'] = {
                'primary_score': org['total_score'],
                'certification_count': org.get('certification_count', 0),
                'alphabetical_position': org['name']
            }
        
        # Update the scored organizations with unique rankings
        self.scored_organizations = sorted_orgs
        
        logger.info(f"Assigned unique rankings to {len(sorted_orgs)} organizations using tie-breaking criteria")
    
    def generate_ranking_statistics(self):
        """Generate comprehensive ranking statistics"""
        logger.info("Generating ranking statistics...")
        
        total_orgs = len(self.scored_organizations)
        scores = [org['total_score'] for org in self.scored_organizations]
        
        # Calculate statistics
        stats = {
            'total_organizations': total_orgs,
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
            },
            'country_breakdown': {},
            'region_breakdown': {},
            'top_10_organizations': self.scored_organizations[:10],
            'generation_timestamp': datetime.now().isoformat()
        }
        
        # Country breakdown
        for org in self.scored_organizations:
            country = org['country']
            if country not in stats['country_breakdown']:
                stats['country_breakdown'][country] = {
                    'count': 0,
                    'average_score': 0,
                    'top_organization': None
                }
            stats['country_breakdown'][country]['count'] += 1
        
        # Calculate country averages
        for country in stats['country_breakdown']:
            country_orgs = [org for org in self.scored_organizations if org['country'] == country]
            if country_orgs:
                avg_score = sum(org['total_score'] for org in country_orgs) / len(country_orgs)
                stats['country_breakdown'][country]['average_score'] = avg_score
                stats['country_breakdown'][country]['top_organization'] = max(country_orgs, key=lambda x: x['total_score'])
        
        self.ranking_results = stats
        return stats
    
    def save_results(self):
        """Save all results to files"""
        logger.info("Saving results to files...")
        
        # Save scored organizations
        with open('scored_organizations_complete.json', 'w', encoding='utf-8') as f:
            json.dump(self.scored_organizations, f, indent=2, ensure_ascii=False)
        
        # Save ranking statistics
        with open('ranking_statistics.json', 'w', encoding='utf-8') as f:
            json.dump(self.ranking_results, f, indent=2, ensure_ascii=False)
        
        # Save a summary report
        summary = {
            'total_organizations_processed': len(self.scored_organizations),
            'average_score': self.ranking_results['average_score'],
            'score_distribution': self.ranking_results['score_distribution'],
            'top_10_organizations': [
                {
                    'rank': i + 1,
                    'name': org['name'],
                    'country': org['country'],
                    'total_score': org['total_score'],
                    'percentile': org['percentile']
                }
                for i, org in enumerate(self.scored_organizations[:10])
            ],
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open('ranking_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info("Results saved successfully")
    
    def run_complete_batch_scoring(self):
        """Run the complete batch scoring process"""
        logger.info("Starting complete batch scoring process...")
        
        try:
            # Step 1: Process all organizations
            self.process_all_organizations()
            
            # Step 2: Calculate unique rankings
            self.calculate_unique_rankings()
            
            # Step 3: Generate statistics
            self.generate_ranking_statistics()
            
            # Step 4: Save results
            self.save_results()
            
            logger.info("Batch scoring process completed successfully!")
            
            # Print summary
            print(f"\n{'='*60}")
            print("BATCH SCORING COMPLETED")
            print(f"{'='*60}")
            print(f"Total Organizations Processed: {len(self.scored_organizations)}")
            print(f"Average Score: {self.ranking_results['average_score']:.2f}")
            print(f"Highest Score: {self.ranking_results['highest_score']:.2f}")
            print(f"Lowest Score: {self.ranking_results['lowest_score']:.2f}")
            print(f"\nTop 5 Organizations:")
            for i, org in enumerate(self.scored_organizations[:5]):
                print(f"{i+1}. {org['name']} ({org['country']}) - Score: {org['total_score']:.2f}")
            print(f"\nFiles Generated:")
            print("- scored_organizations_complete.json")
            print("- ranking_statistics.json")
            print("- ranking_summary.json")
            
        except Exception as e:
            logger.error(f"Error in batch scoring process: {e}")
            raise

def main():
    """Main function to run the batch scoring system"""
    try:
        batch_scorer = BatchScoringSystem()
        batch_scorer.run_complete_batch_scoring()
    except Exception as e:
        logger.error(f"Failed to run batch scoring: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())