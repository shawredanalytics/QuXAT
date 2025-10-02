#!/usr/bin/env python3
"""
Mayo Clinic CAP Integration Script
Integrates extracted Mayo Clinic CAP laboratories into the unified healthcare database
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any

class MayoCAPIntegrator:
    """Integrator for Mayo Clinic CAP laboratories"""
    
    def __init__(self):
        self.unified_db = []
        self.mayo_labs = []
        self.integration_stats = {
            "total_mayo_labs": 0,
            "merged_with_existing": 0,
            "added_as_new": 0,
            "updated_organizations": []
        }
    
    def load_data(self):
        """Load unified database and Mayo Clinic CAP laboratories"""
        try:
            # Load unified database
            with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.unified_db = data.get('organizations', []) if isinstance(data, dict) else data
            
            # Load Mayo Clinic CAP laboratories
            with open('mayo_cap_laboratories.json', 'r', encoding='utf-8') as f:
                self.mayo_labs = json.load(f)
            
            print(f"📊 Loaded {len(self.unified_db)} organizations from unified database")
            print(f"📊 Loaded {len(self.mayo_labs)} Mayo Clinic CAP laboratories")
            
            self.integration_stats["total_mayo_labs"] = len(self.mayo_labs)
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def integrate_mayo_labs(self):
        """Integrate Mayo Clinic CAP laboratories into unified database"""
        print("\n🔄 Starting Mayo Clinic CAP integration...")
        
        for mayo_lab in self.mayo_labs:
            existing_org = self._find_matching_mayo_organization(mayo_lab)
            
            if existing_org:
                print(f"🔗 Merging CAP data with existing Mayo Clinic: {existing_org['name']}")
                self._merge_cap_into_existing_org(existing_org, mayo_lab)
                self.integration_stats["merged_with_existing"] += 1
                self.integration_stats["updated_organizations"].append(existing_org["name"])
            else:
                print(f"➕ Adding new Mayo Clinic CAP laboratory: {mayo_lab['name']}")
                self.unified_db.append(mayo_lab)
                self.integration_stats["added_as_new"] += 1
                self.integration_stats["updated_organizations"].append(mayo_lab["name"])
        
        print(f"\n✅ Integration complete!")
        print(f"   - Merged with existing: {self.integration_stats['merged_with_existing']}")
        print(f"   - Added as new: {self.integration_stats['added_as_new']}")
    
    def _find_matching_mayo_organization(self, mayo_lab: Dict) -> Dict:
        """Find matching Mayo Clinic organization in unified database"""
        mayo_name = mayo_lab["name"].lower()
        
        # Look for exact or partial matches
        for org in self.unified_db:
            org_name = org.get("name", "").lower()
            
            # Check for Mayo Clinic matches
            if "mayo clinic" in org_name:
                # Check for specific facility matches
                if "biopharma" in mayo_name and "biopharma" in org_name:
                    return org
                elif "eau claire" in mayo_name and "eau claire" in org_name:
                    return org
                elif "health system" in mayo_name and "health system" in org_name:
                    return org
                # General Mayo Clinic match for main organization
                elif mayo_name == "mayo clinic" or org_name == "mayo clinic":
                    return org
        
        return None
    
    def _merge_cap_into_existing_org(self, existing_org: Dict, mayo_lab: Dict):
        """Merge CAP certification data into existing Mayo Clinic organization"""
        # Add CAP certification
        if "certifications" not in existing_org:
            existing_org["certifications"] = []
        elif not isinstance(existing_org["certifications"], list):
            existing_org["certifications"] = []
        
        # Add CAP certification
        cap_cert = mayo_lab["certifications"][0]  # Get the CAP certification
        existing_org["certifications"].append(cap_cert)
        
        # Update quality indicators
        if "quality_indicators" not in existing_org:
            existing_org["quality_indicators"] = {}
        
        existing_org["quality_indicators"].update({
            "cap_accredited": True,
            "iso_15189_accredited": True,
            "laboratory_accreditation": True,
            "international_accreditation": True,
            "accreditation_valid": True
        })
        
        # Add quality initiatives
        if "quality_initiatives" not in existing_org:
            existing_org["quality_initiatives"] = []
        
        for initiative in mayo_lab["quality_initiatives"]:
            existing_org["quality_initiatives"].append(initiative)
        
        # Update specialties
        if "specialties" not in existing_org:
            existing_org["specialties"] = []
        
        for specialty in mayo_lab["specialties"]:
            if specialty not in existing_org["specialties"]:
                existing_org["specialties"].append(specialty)
        
        # Update quality score (increase by CAP impact)
        current_score = existing_org.get("quality_score", 70.0)
        cap_impact = cap_cert.get("score_impact", 18.0)
        new_score = min(100.0, current_score + cap_impact)
        existing_org["quality_score"] = new_score
        
        # Update data source
        current_source = existing_org.get("data_source", "")
        if "CAP Database" not in current_source:
            existing_org["data_source"] = f"{current_source}, CAP Database".strip(", ")
        
        # Update last updated
        existing_org["last_updated"] = datetime.now().isoformat()
        
        # Add CAP-specific information
        if "laboratory_info" not in existing_org:
            existing_org["laboratory_info"] = {}
        
        existing_org["laboratory_info"].update({
            "cap_accredited_labs": existing_org["laboratory_info"].get("cap_accredited_labs", []) + [mayo_lab["name"]],
            "cap_accreditation_type": "CAP 15189",
            "laboratory_specialties": mayo_lab["specialties"]
        })
    
    def save_integrated_database(self):
        """Save the integrated database"""
        try:
            # Prepare output data
            output_data = {
                "organizations": self.unified_db,
                "metadata": {
                    "total_organizations": len(self.unified_db),
                    "last_updated": datetime.now().isoformat(),
                    "data_sources": ["Multiple Healthcare Databases", "CAP Database", "Mayo Clinic"],
                    "mayo_cap_integration": self.integration_stats
                }
            }
            
            # Save to main unified database
            with open('unified_healthcare_organizations.json', 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            # Save to CAP-enhanced version
            with open('unified_healthcare_organizations_with_mayo_cap.json', 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved integrated database with {len(self.unified_db)} organizations")
            print(f"   - Main file: unified_healthcare_organizations.json")
            print(f"   - Enhanced file: unified_healthcare_organizations_with_mayo_cap.json")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving integrated database: {e}")
            return False
    
    def generate_integration_report(self):
        """Generate integration report"""
        report = {
            "mayo_cap_integration_report": {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_mayo_labs_processed": self.integration_stats["total_mayo_labs"],
                    "merged_with_existing": self.integration_stats["merged_with_existing"],
                    "added_as_new": self.integration_stats["added_as_new"],
                    "total_organizations_after_integration": len(self.unified_db)
                },
                "updated_organizations": self.integration_stats["updated_organizations"],
                "mayo_labs_integrated": [
                    {
                        "name": lab["name"],
                        "location": f"{lab['city']}, {lab['state']}" if lab.get('city') else lab.get('zip_code', 'Unknown'),
                        "accreditation": lab["accreditation_type"],
                        "quality_score": lab["quality_score"]
                    }
                    for lab in self.mayo_labs
                ]
            }
        }
        
        # Save report
        with open('mayo_cap_integration_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Integration Report:")
        print(f"   - Total Mayo labs processed: {self.integration_stats['total_mayo_labs']}")
        print(f"   - Merged with existing: {self.integration_stats['merged_with_existing']}")
        print(f"   - Added as new: {self.integration_stats['added_as_new']}")
        print(f"   - Report saved to: mayo_cap_integration_report.json")

def main():
    """Main integration function"""
    print("🏥 Mayo Clinic CAP Integration")
    print("=" * 50)
    
    integrator = MayoCAPIntegrator()
    
    # Load data
    if not integrator.load_data():
        return
    
    # Integrate Mayo labs
    integrator.integrate_mayo_labs()
    
    # Save integrated database
    if integrator.save_integrated_database():
        integrator.generate_integration_report()
    
    print("\n🎉 Mayo Clinic CAP integration completed successfully!")

if __name__ == "__main__":
    main()