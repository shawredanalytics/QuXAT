import json
import pandas as pd
from datetime import datetime
import os

class RankingReportGenerator:
    def __init__(self):
        self.scored_organizations = []
        self.ranking_statistics = {}
        
    def load_data(self):
        """Load scored organizations and ranking statistics"""
        try:
            with open('scored_organizations_complete.json', 'r') as f:
                self.scored_organizations = json.load(f)
            
            with open('ranking_statistics.json', 'r') as f:
                self.ranking_statistics = json.load(f)
                
            print(f"Loaded {len(self.scored_organizations)} organizations")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def generate_excel_report(self):
        """Generate comprehensive Excel report with multiple sheets"""
        print("Generating comprehensive Excel report...")
        
        # Create Excel writer
        filename = f"QuXAT_Comprehensive_Ranking_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            
            # Sheet 1: Complete Rankings
            df_complete = pd.DataFrame(self.scored_organizations)
            
            # Select and reorder columns for the main report
            main_columns = [
                'overall_rank', 'name', 'country', 'region', 'hospital_type',
                'total_score', 'percentile', 'certification_score', 
                'quality_initiatives_score', 'patient_feedback_score',
                'certification_count', 'last_updated'
            ]
            
            df_main = df_complete[main_columns].copy()
            df_main = df_main.sort_values('overall_rank')
            
            # Format columns
            df_main['percentile'] = df_main['percentile'].round(2)
            df_main['total_score'] = df_main['total_score'].round(2)
            df_main['certification_score'] = df_main['certification_score'].round(2)
            df_main['quality_initiatives_score'] = df_main['quality_initiatives_score'].round(2)
            df_main['patient_feedback_score'] = df_main['patient_feedback_score'].round(2)
            
            df_main.to_excel(writer, sheet_name='Complete Rankings', index=False)
            
            # Sheet 2: Top 100 Organizations
            df_top100 = df_main.head(100)
            df_top100.to_excel(writer, sheet_name='Top 100', index=False)
            
            # Sheet 3: Country-wise Rankings
            country_summary = df_main.groupby('country').agg({
                'overall_rank': ['count', 'min', 'mean'],
                'total_score': ['mean', 'max', 'min'],
                'percentile': ['mean', 'max', 'min']
            }).round(2)
            
            country_summary.columns = [
                'Total_Orgs', 'Best_Rank', 'Avg_Rank',
                'Avg_Score', 'Max_Score', 'Min_Score',
                'Avg_Percentile', 'Max_Percentile', 'Min_Percentile'
            ]
            
            country_summary = country_summary.sort_values('Best_Rank')
            country_summary.to_excel(writer, sheet_name='Country Summary')
            
            # Sheet 4: Score Distribution
            score_ranges = [
                (70, 100, 'A+ (70-100)'),
                (60, 69.99, 'A (60-69)'),
                (50, 59.99, 'B+ (50-59)'),
                (40, 49.99, 'B (40-49)'),
                (30, 39.99, 'C+ (30-39)'),
                (0, 29.99, 'C (0-29)')
            ]
            
            distribution_data = []
            for min_score, max_score, grade in score_ranges:
                count = len(df_main[(df_main['total_score'] >= min_score) & 
                                  (df_main['total_score'] <= max_score)])
                percentage = (count / len(df_main)) * 100
                distribution_data.append({
                    'Grade': grade,
                    'Score_Range': f"{min_score}-{max_score}",
                    'Count': count,
                    'Percentage': round(percentage, 2)
                })
            
            df_distribution = pd.DataFrame(distribution_data)
            df_distribution.to_excel(writer, sheet_name='Score Distribution', index=False)
            
            # Sheet 5: Regional Analysis
            if 'region' in df_main.columns:
                regional_summary = df_main.groupby('region').agg({
                    'overall_rank': ['count', 'min', 'mean'],
                    'total_score': ['mean', 'max', 'min'],
                    'percentile': ['mean', 'max', 'min']
                }).round(2)
                
                regional_summary.columns = [
                    'Total_Orgs', 'Best_Rank', 'Avg_Rank',
                    'Avg_Score', 'Max_Score', 'Min_Score',
                    'Avg_Percentile', 'Max_Percentile', 'Min_Percentile'
                ]
                
                regional_summary = regional_summary.sort_values('Best_Rank')
                regional_summary.to_excel(writer, sheet_name='Regional Summary')
        
        print(f"Excel report generated: {filename}")
        return filename
    
    def generate_csv_reports(self):
        """Generate CSV reports for easy data analysis"""
        print("Generating CSV reports...")
        
        # Main ranking report
        df_complete = pd.DataFrame(self.scored_organizations)
        main_columns = [
            'overall_rank', 'name', 'country', 'region', 'hospital_type',
            'total_score', 'percentile', 'certification_score', 
            'quality_initiatives_score', 'patient_feedback_score',
            'certification_count'
        ]
        
        df_main = df_complete[main_columns].copy()
        df_main = df_main.sort_values('overall_rank')
        
        # Format numeric columns
        numeric_columns = ['percentile', 'total_score', 'certification_score', 
                          'quality_initiatives_score', 'patient_feedback_score']
        for col in numeric_columns:
            df_main[col] = df_main[col].round(2)
        
        csv_filename = f"QuXAT_Complete_Rankings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df_main.to_csv(csv_filename, index=False)
        
        print(f"CSV report generated: {csv_filename}")
        return csv_filename
    
    def generate_summary_report(self):
        """Generate a text summary report"""
        print("Generating summary report...")
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("QuXAT HEALTHCARE ORGANIZATION RANKING REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Overall statistics
        total_orgs = len(self.scored_organizations)
        scores = [org['total_score'] for org in self.scored_organizations]
        
        report_lines.append("OVERALL STATISTICS")
        report_lines.append("-" * 40)
        report_lines.append(f"Total Organizations Ranked: {total_orgs:,}")
        report_lines.append(f"Average Score: {sum(scores)/len(scores):.2f}")
        report_lines.append(f"Highest Score: {max(scores):.2f}")
        report_lines.append(f"Lowest Score: {min(scores):.2f}")
        report_lines.append("")
        
        # Top 10 organizations
        sorted_orgs = sorted(self.scored_organizations, key=lambda x: x['overall_rank'])
        
        report_lines.append("TOP 10 HEALTHCARE ORGANIZATIONS")
        report_lines.append("-" * 40)
        report_lines.append(f"{'Rank':<6} {'Score':<8} {'Percentile':<12} {'Organization'}")
        report_lines.append("-" * 80)
        
        for i, org in enumerate(sorted_orgs[:10]):
            report_lines.append(f"{org['overall_rank']:<6} {org['total_score']:<8.1f} {org['percentile']:<12.2f}% {org['name']}")
        
        report_lines.append("")
        
        # Country breakdown
        country_stats = {}
        for org in self.scored_organizations:
            country = org['country']
            if country not in country_stats:
                country_stats[country] = {'count': 0, 'scores': []}
            country_stats[country]['count'] += 1
            country_stats[country]['scores'].append(org['total_score'])
        
        report_lines.append("COUNTRY-WISE BREAKDOWN")
        report_lines.append("-" * 40)
        report_lines.append(f"{'Country':<20} {'Count':<8} {'Avg Score':<12} {'Best Score'}")
        report_lines.append("-" * 60)
        
        for country, stats in sorted(country_stats.items(), key=lambda x: max(x[1]['scores']), reverse=True):
            avg_score = sum(stats['scores']) / len(stats['scores'])
            best_score = max(stats['scores'])
            report_lines.append(f"{country:<20} {stats['count']:<8} {avg_score:<12.2f} {best_score:.2f}")
        
        # Save summary report
        summary_filename = f"QuXAT_Summary_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"Summary report generated: {summary_filename}")
        return summary_filename
    
    def run_complete_report_generation(self):
        """Run the complete report generation process"""
        print("Starting comprehensive ranking report generation...")
        
        if not self.load_data():
            print("Failed to load data. Exiting.")
            return
        
        # Generate all reports
        excel_file = self.generate_excel_report()
        csv_file = self.generate_csv_reports()
        summary_file = self.generate_summary_report()
        
        print("\n" + "="*60)
        print("RANKING REPORT GENERATION COMPLETED")
        print("="*60)
        print(f"Files generated:")
        print(f"1. Excel Report: {excel_file}")
        print(f"2. CSV Report: {csv_file}")
        print(f"3. Summary Report: {summary_file}")
        print(f"\nAll {len(self.scored_organizations)} healthcare organizations have been ranked")
        print("with unique ranks and percentile scores based on QuXAT scoring logic.")

if __name__ == "__main__":
    generator = RankingReportGenerator()
    generator.run_complete_report_generation()