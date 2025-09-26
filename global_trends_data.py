"""
Global Healthcare Quality Trends Data Generator
Generates realistic month-wise accreditation/certification data for the past 3 years
"""

import json
import random
from datetime import datetime, timedelta
from collections import defaultdict

def generate_global_trends_data():
    """Generate comprehensive global healthcare quality trends data"""
    
    # Define certification types and their characteristics
    certification_types = {
        "JCI": {
            "name": "Joint Commission International",
            "growth_rate": 0.15,  # 15% annual growth
            "seasonal_pattern": [0.8, 0.9, 1.2, 1.1, 1.0, 0.9, 0.8, 0.9, 1.3, 1.2, 1.1, 1.0],
            "base_monthly": 45
        },
        "NABH": {
            "name": "National Accreditation Board for Hospitals",
            "growth_rate": 0.25,  # 25% annual growth
            "seasonal_pattern": [1.0, 1.1, 1.3, 1.2, 1.0, 0.8, 0.7, 0.9, 1.4, 1.3, 1.2, 1.1],
            "base_monthly": 35
        },
        "CAP": {
            "name": "College of American Pathologists",
            "growth_rate": 0.12,  # 12% annual growth
            "seasonal_pattern": [0.9, 1.0, 1.1, 1.2, 1.1, 0.9, 0.8, 0.9, 1.2, 1.3, 1.1, 1.0],
            "base_monthly": 25
        },
        "ISO": {
            "name": "ISO Healthcare Standards",
            "growth_rate": 0.18,  # 18% annual growth
            "seasonal_pattern": [1.1, 1.2, 1.0, 0.9, 1.0, 1.1, 1.0, 0.9, 1.2, 1.3, 1.1, 1.0],
            "base_monthly": 30
        },
        "AAAHC": {
            "name": "Accreditation Association for Ambulatory Health Care",
            "growth_rate": 0.20,  # 20% annual growth
            "seasonal_pattern": [0.9, 1.0, 1.2, 1.3, 1.1, 0.8, 0.7, 0.9, 1.3, 1.2, 1.1, 1.0],
            "base_monthly": 20
        }
    }
    
    # Define regions and their distribution
    regions = {
        "North America": 0.25,
        "Europe": 0.22,
        "Asia-Pacific": 0.30,
        "Middle East & Africa": 0.12,
        "Latin America": 0.11
    }
    
    # Generate data for the past 3 years (2022-2024)
    trends_data = {
        "monthly_accreditations": [],
        "certification_breakdown": [],
        "regional_distribution": [],
        "yearly_summary": [],
        "growth_metrics": {},
        "metadata": {
            "generated_date": datetime.now().isoformat(),
            "data_period": "2022-2024",
            "total_months": 36
        }
    }
    
    # Generate monthly data
    start_date = datetime(2022, 1, 1)
    
    for month_offset in range(36):  # 36 months (3 years)
        current_date = start_date + timedelta(days=30 * month_offset)
        year = current_date.year
        month = current_date.month
        
        monthly_data = {
            "year": year,
            "month": month,
            "month_name": current_date.strftime("%B"),
            "date": current_date.strftime("%Y-%m-%d"),
            "certifications": {}
        }
        
        total_monthly_accreditations = 0
        
        # Generate data for each certification type
        for cert_code, cert_info in certification_types.items():
            # Calculate base count with growth over time
            years_from_start = (year - 2022) + (month - 1) / 12
            growth_factor = (1 + cert_info["growth_rate"]) ** years_from_start
            
            # Apply seasonal pattern
            seasonal_multiplier = cert_info["seasonal_pattern"][month - 1]
            
            # Add some randomness
            random_factor = random.uniform(0.8, 1.2)
            
            # Calculate final count
            base_count = cert_info["base_monthly"]
            monthly_count = int(base_count * growth_factor * seasonal_multiplier * random_factor)
            
            monthly_data["certifications"][cert_code] = {
                "name": cert_info["name"],
                "count": monthly_count,
                "cumulative": 0  # Will be calculated later
            }
            
            total_monthly_accreditations += monthly_count
        
        monthly_data["total_accreditations"] = total_monthly_accreditations
        trends_data["monthly_accreditations"].append(monthly_data)
    
    # Calculate cumulative data
    cumulative_counts = defaultdict(int)
    for month_data in trends_data["monthly_accreditations"]:
        for cert_code, cert_data in month_data["certifications"].items():
            cumulative_counts[cert_code] += cert_data["count"]
            cert_data["cumulative"] = cumulative_counts[cert_code]
    
    # Generate certification breakdown summary
    for cert_code, cert_info in certification_types.items():
        total_count = cumulative_counts[cert_code]
        trends_data["certification_breakdown"].append({
            "certification_type": cert_code,
            "name": cert_info["name"],
            "total_accreditations": total_count,
            "percentage": round((total_count / sum(cumulative_counts.values())) * 100, 1),
            "average_monthly": round(total_count / 36, 1),
            "growth_rate": cert_info["growth_rate"] * 100
        })
    
    # Generate regional distribution
    total_accreditations = sum(cumulative_counts.values())
    for region, percentage in regions.items():
        region_count = int(total_accreditations * percentage)
        trends_data["regional_distribution"].append({
            "region": region,
            "total_accreditations": region_count,
            "percentage": round(percentage * 100, 1),
            "monthly_average": round(region_count / 36, 1)
        })
    
    # Generate yearly summary
    yearly_totals = defaultdict(int)
    for month_data in trends_data["monthly_accreditations"]:
        yearly_totals[month_data["year"]] += month_data["total_accreditations"]
    
    for year in [2022, 2023, 2024]:
        if year in yearly_totals:
            trends_data["yearly_summary"].append({
                "year": year,
                "total_accreditations": yearly_totals[year],
                "monthly_average": round(yearly_totals[year] / 12, 1),
                "growth_from_previous": 0 if year == 2022 else round(
                    ((yearly_totals[year] - yearly_totals[year-1]) / yearly_totals[year-1]) * 100, 1
                )
            })
    
    # Generate growth metrics
    trends_data["growth_metrics"] = {
        "overall_growth_rate": round(
            ((yearly_totals[2024] - yearly_totals[2022]) / yearly_totals[2022]) * 100, 1
        ),
        "compound_annual_growth_rate": round(
            (((yearly_totals[2024] / yearly_totals[2022]) ** (1/2)) - 1) * 100, 1
        ),
        "total_accreditations_3_years": sum(yearly_totals.values()),
        "peak_month": max(trends_data["monthly_accreditations"], 
                         key=lambda x: x["total_accreditations"]),
        "lowest_month": min(trends_data["monthly_accreditations"], 
                           key=lambda x: x["total_accreditations"])
    }
    
    return trends_data

def save_trends_data():
    """Generate and save the trends data to a JSON file"""
    trends_data = generate_global_trends_data()
    
    with open('global_healthcare_trends_2022_2024.json', 'w', encoding='utf-8') as f:
        json.dump(trends_data, f, indent=2, ensure_ascii=False)
    
    print(f"Global healthcare trends data generated successfully!")
    print(f"Total accreditations over 3 years: {trends_data['growth_metrics']['total_accreditations_3_years']:,}")
    print(f"Overall growth rate: {trends_data['growth_metrics']['overall_growth_rate']}%")
    print(f"CAGR: {trends_data['growth_metrics']['compound_annual_growth_rate']}%")
    
    return trends_data

if __name__ == "__main__":
    save_trends_data()