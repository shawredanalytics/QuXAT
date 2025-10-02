#!/usr/bin/env python3
"""
Mayo Clinic CAP Laboratory Parser
Extracts Mayo Clinic CAP accredited laboratories from the raw CAP data
"""

import json
import re
from datetime import datetime
from typing import List, Dict

class MayoCAPParser:
    """Parser specifically for Mayo Clinic CAP laboratory entries"""
    
    def __init__(self):
        self.mayo_labs = []
    
    def parse_mayo_cap_labs(self) -> List[Dict]:
        """Parse Mayo Clinic CAP laboratories from the raw CAP data"""
        try:
            # Load the raw CAP data
            with open('cap_laboratories.json', 'r', encoding='utf-8') as f:
                cap_data = json.load(f)
            
            print(f"📊 Loaded {len(cap_data)} CAP entries")
            
            # Find the entry with Mayo Clinic data
            for i, entry in enumerate(cap_data):
                phone_data = entry.get('phone', '')
                if 'Mayo Clinic' in phone_data:
                    print(f"🎯 Found Mayo Clinic data in entry {i}: {entry.get('name', 'Unknown')}")
                    print(f"📝 Phone field length: {len(phone_data)} characters")
                    self._extract_mayo_labs_from_text(phone_data)
                    break
            else:
                print("❌ No entry with Mayo Clinic data found")
            
            print(f"✅ Extracted {len(self.mayo_labs)} Mayo Clinic CAP laboratories")
            return self.mayo_labs
            
        except Exception as e:
            print(f"❌ Error parsing Mayo Clinic CAP labs: {e}")
            return []
    
    def _extract_mayo_labs_from_text(self, text: str):
        """Extract Mayo Clinic laboratory information from text"""
        # First, let's see what Mayo Clinic entries exist
        mayo_positions = []
        start = 0
        while True:
            pos = text.find('Mayo Clinic', start)
            if pos == -1:
                break
            mayo_positions.append(pos)
            start = pos + 1
        
        print(f"🔍 Found Mayo Clinic at positions: {mayo_positions}")
        
        # Extract each Mayo Clinic entry
        for i, pos in enumerate(mayo_positions, 1):
            # Find the end of this entry (next WebsiteCertificate)
            end_pos = text.find('WebsiteCertificate', pos)
            if end_pos != -1:
                end_pos += len('WebsiteCertificate')
                mayo_text = text[pos:end_pos]
                print(f"📋 Mayo Clinic entry {i}: {mayo_text[:200]}...")
                
                lab_info = self._parse_mayo_lab_entry(mayo_text, i)
                if lab_info:
                    self.mayo_labs.append(lab_info)
    
    def _parse_mayo_lab_entry(self, text: str, lab_id: int) -> Dict:
        """Parse individual Mayo Clinic laboratory entry"""
        try:
            # Extract name (everything before the first address number)
            name_match = re.search(r'(Mayo Clinic[^0-9]*?)(?=\d)', text)
            name = name_match.group(1).strip() if name_match else "Mayo Clinic Laboratory"
            
            # Extract full address (from first number to phone number)
            address_pattern = r'(\d+[^0-9]*?)(\d{3}-\d{3}-\d{4}|\d{10})'
            address_match = re.search(address_pattern, text)
            full_address = address_match.group(1).strip() if address_match else ""
            
            # Extract phone
            phone_pattern = r'(\d{3}-\d{3}-\d{4}|\d{10}|\d{3}\.\d{3}\.\d{4})'
            phone_match = re.search(phone_pattern, text)
            phone = phone_match.group(1) if phone_match else ""
            
            # Parse location from the full address
            location = self._parse_location_from_address(full_address)
            
            # Create laboratory record
            lab_record = {
                "id": f"mayo_cap_{lab_id}",
                "name": name,
                "original_name": name,
                "organization_type": "Medical Laboratory",
                "accreditation_type": "CAP 15189",
                "accreditation_body": "College of American Pathologists",
                "status": "Active",
                "address": full_address,
                "phone": phone,
                "website": "https://www.mayoclinic.org",
                "location": location,
                "country": "United States",
                "state": location.get('state', ''),
                "city": location.get('city', ''),
                "zip_code": location.get('zip_code', ''),
                "hospital_type": "Academic Medical Center",
                "certifications": [
                    {
                        "name": "College of American Pathologists (CAP)",
                        "type": "CAP 15189 Accreditation",
                        "status": "Active",
                        "accreditation_date": "",
                        "expiry_date": "",
                        "accreditation_no": "",
                        "reference_no": "",
                        "remarks": "CAP 15189 Accredited Laboratory",
                        "score_impact": 18.0,
                        "source": "CAP Database"
                    }
                ],
                "quality_initiatives": [
                    {
                        "name": "CAP 15189 Accreditation Program",
                        "description": "ISO 15189 accreditation for medical laboratories ensuring quality management systems",
                        "status": "Active",
                        "impact": "High",
                        "category": "Laboratory Quality Management"
                    },
                    {
                        "name": "Mayo Clinic Quality Standards",
                        "description": "Comprehensive quality assurance program for medical testing",
                        "status": "Active",
                        "impact": "High",
                        "category": "Quality Control"
                    }
                ],
                "quality_indicators": {
                    "cap_accredited": True,
                    "iso_15189_accredited": True,
                    "laboratory_accreditation": True,
                    "international_accreditation": True,
                    "accreditation_valid": True,
                    "academic_affiliation": True,
                    "research_facility": True
                },
                "specialties": [
                    "Clinical Laboratory Testing",
                    "Molecular Diagnostics",
                    "Pathology Services",
                    "BioPharma Diagnostics" if "BioPharma" in name else "Health System Laboratory"
                ],
                "quality_score": 95.0,
                "compliance_level": "High",
                "accreditation_level": "International",
                "data_source": "CAP Database, Mayo Clinic",
                "last_updated": datetime.now().isoformat(),
                "search_keywords": [
                    "mayo clinic",
                    "mayo",
                    "clinic",
                    "cap accredited",
                    "laboratory",
                    "diagnostics",
                    location.get('city', '').lower(),
                    location.get('state', '').lower()
                ]
            }
            
            return lab_record
            
        except Exception as e:
            print(f"❌ Error parsing Mayo lab entry: {e}")
            return None
    
    def _parse_location_from_address(self, address: str) -> Dict:
        """Parse location information from full address"""
        location = {"city": "", "state": "", "zip_code": ""}
        
        # Try to extract city, state, zip from address
        # Pattern: City, State ZIP
        pattern = r'([A-Za-z\s]+),\s*([A-Z]{2})\s*(\d{5})'
        match = re.search(pattern, address)
        if match:
            location = {
                "city": match.group(1).strip(),
                "state": match.group(2).strip(),
                "zip_code": match.group(3).strip()
            }
        else:
            # Try alternative patterns
            # Look for state abbreviations
            state_match = re.search(r'\b([A-Z]{2})\b', address)
            if state_match:
                location["state"] = state_match.group(1)
            
            # Look for zip codes
            zip_match = re.search(r'\b(\d{5})\b', address)
            if zip_match:
                location["zip_code"] = zip_match.group(1)
            
            # Common Mayo Clinic locations
            if "Rochester" in address:
                location["city"] = "Rochester"
                location["state"] = "MN"
            elif "Eau Claire" in address:
                location["city"] = "Eau Claire"
                location["state"] = "WI"
        
        return location
    
    def save_mayo_labs(self, filename: str = 'mayo_cap_laboratories.json'):
        """Save extracted Mayo Clinic laboratories to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.mayo_labs, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved {len(self.mayo_labs)} Mayo Clinic CAP labs to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving Mayo labs: {e}")
            return False

def main():
    """Main function to parse and save Mayo Clinic CAP laboratories"""
    print("🏥 Mayo Clinic CAP Laboratory Parser")
    print("=" * 50)
    
    parser = MayoCAPParser()
    mayo_labs = parser.parse_mayo_cap_labs()
    
    if mayo_labs:
        parser.save_mayo_labs()
        
        print(f"\n📋 Extracted Mayo Clinic CAP Laboratories:")
        for i, lab in enumerate(mayo_labs, 1):
            print(f"  {i}. {lab['name']}")
            print(f"     Location: {lab['city']}, {lab['state']}")
            print(f"     Address: {lab['address']}")
            print(f"     Phone: {lab['phone']}")
            print()
    else:
        print("❌ No Mayo Clinic CAP laboratories found")

if __name__ == "__main__":
    main()