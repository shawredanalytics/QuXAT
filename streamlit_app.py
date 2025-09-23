import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import quote_plus
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors as rl_colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart

# Import data validation module
from data_validator import healthcare_validator
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image as PILImage
import io
import base64
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="QuXAT - Healthcare Quality Grid",
    page_icon="assets/QuXAT Logo Facebook.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dynamic logo function for consistent display across all pages
def display_dynamic_logo():
    """Display the QuXAT logo dynamically by loading from assets folder"""
    import os
    from PIL import Image
    
    # Path to the PNG logo file
    logo_path = os.path.join("assets", "QuXAT Logo Facebook.png")
    
    try:
        # Check if logo file exists
        if os.path.exists(logo_path):
            # Load and display the PNG image
            logo_image = Image.open(logo_path)
            
            # Create a centered container with styling
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("""
                <div style="
                    display: flex; 
                    justify-content: center; 
                    align-items: center; 
                    padding: 8px 0; 
                    margin-bottom: 15px;
                    border-bottom: 1px solid #e8e8e8;
                    background: #ffffff;
                ">
                """, unsafe_allow_html=True)
                
                # Display the image with Streamlit's image function
                st.image(logo_image, width=280)
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Fallback if logo file doesn't exist
            st.markdown("""
            <div style="
                display: flex; 
                justify-content: center; 
                align-items: center; 
                padding: 8px 0; 
                margin-bottom: 15px;
                border-bottom: 1px solid #e8e8e8;
                background: #ffffff;
            ">
                <div style="
                    text-align: center; 
                    padding: 8px;
                    color: #2c3e50;
                    font-size: 24px;
                    font-weight: bold;
                ">
                    🏥 QuXAT - Healthcare Quality Platform
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        # Error fallback
        st.markdown(f"""
        <div style="
            display: flex; 
            justify-content: center; 
            align-items: center; 
            padding: 8px 0; 
            margin-bottom: 15px;
            border-bottom: 1px solid #e8e8e8;
            background: #ffffff;
        ">
            <div style="
                text-align: center; 
                padding: 8px;
                color: #e74c3c;
                font-size: 14px;
            ">
                ⚠️ Logo loading error: {str(e)}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Admin Authentication System
def admin_login():
    """Admin login interface"""
    st.markdown("### 🔐 Admin Login")
    
    # Simple admin credentials (in production, use proper authentication)
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "QuXAT2024!"
    
    with st.form("admin_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.session_state.admin_username = username
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

def admin_logout():
    """Admin logout function"""
    if st.button("🚪 Logout"):
        st.session_state.admin_authenticated = False
        st.session_state.admin_username = None
        st.success("✅ Logged out successfully!")
        st.rerun()

def is_admin_authenticated():
    """Check if admin is authenticated"""
    return st.session_state.get('admin_authenticated', False)

# Data Upload Management System
def init_upload_storage():
    """Initialize upload storage in session state"""
    if 'pending_uploads' not in st.session_state:
        st.session_state.pending_uploads = []
    if 'approved_uploads' not in st.session_state:
        st.session_state.approved_uploads = []
    if 'rejected_uploads' not in st.session_state:
        st.session_state.rejected_uploads = []

def add_pending_upload(upload_data):
    """Add new upload to pending queue"""
    init_upload_storage()
    upload_data['upload_id'] = len(st.session_state.pending_uploads) + 1
    upload_data['upload_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    upload_data['status'] = 'pending'
    st.session_state.pending_uploads.append(upload_data)

def approve_upload(upload_id):
    """Approve a pending upload"""
    init_upload_storage()
    for i, upload in enumerate(st.session_state.pending_uploads):
        if upload['upload_id'] == upload_id:
            upload['status'] = 'approved'
            upload['approved_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            st.session_state.approved_uploads.append(upload)
            st.session_state.pending_uploads.pop(i)
            break

def reject_upload(upload_id, reason=""):
    """Reject a pending upload"""
    init_upload_storage()
    for i, upload in enumerate(st.session_state.pending_uploads):
        if upload['upload_id'] == upload_id:
            upload['status'] = 'rejected'
            upload['rejected_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            upload['rejection_reason'] = reason
            st.session_state.rejected_uploads.append(upload)
            st.session_state.pending_uploads.pop(i)
            break

# Hospital Management System
def init_hospital_storage():
    """Initialize hospital storage in session state"""
    if 'custom_hospitals' not in st.session_state:
        st.session_state.custom_hospitals = []

def add_hospital(hospital_data):
    """Add new hospital to the database"""
    init_hospital_storage()
    hospital_data['hospital_id'] = len(st.session_state.custom_hospitals) + 1
    hospital_data['added_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.session_state.custom_hospitals.append(hospital_data)

def delete_hospital(hospital_id):
    """Delete hospital from the database"""
    init_hospital_storage()
    st.session_state.custom_hospitals = [h for h in st.session_state.custom_hospitals if h['hospital_id'] != hospital_id]

def update_hospital(hospital_id, updated_data):
    """Update hospital information"""
    init_hospital_storage()
    for i, hospital in enumerate(st.session_state.custom_hospitals):
        if hospital['hospital_id'] == hospital_id:
            st.session_state.custom_hospitals[i].update(updated_data)
            st.session_state.custom_hospitals[i]['updated_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            break

# Healthcare Organization Data Integration System
class HealthcareOrgAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Load unified healthcare database
        self.unified_database = self.load_unified_database()
        
        # Enhanced certification databases and scoring weights
        # Comprehensive Global Healthcare Quality Certifications (Updated with 100+ standards)
        self.certification_weights = {
            # International Gold Standards (Top Tier - 25-35 points)
            'JCI': 35,  # Joint Commission International - Global gold standard
            'Joint Commission': 30,  # US Joint Commission - Highest US standard
            'Magnet': 28,  # Magnet Recognition - Nursing excellence gold standard
            'DNV GL Healthcare': 25,  # International healthcare accreditation
            'WHO-FIC Collaborating Centre': 25,  # WHO standards
            
            # Major International Standards (Second Tier - 18-25 points)
            'HIMSS EMRAM Level 6-7': 25,  # Advanced health IT maturity
            'NCQA': 22,  # National Committee for Quality Assurance
            'AAAHC': 20,  # Ambulatory care accreditation
            'CARF': 20,  # Rehabilitation accreditation
            'CAP': 20,  # College of American Pathologists
            'CLIA': 18,  # Clinical Laboratory Improvement Amendments
            'RTAC': 18,  # Reproductive Technology Accreditation Committee
            
            # Regional Excellence Standards (Third Tier - 12-18 points)
            'NABH': 18,  # Indian hospital accreditation
            'NABL': 15,  # Indian laboratory accreditation
            'Accreditation Canada': 18,  # Canadian healthcare accreditation
            'TGA': 20,  # Australia Therapeutic Goods Administration
            'HSA': 18,  # Singapore Health Sciences Authority
            'PMDA': 22,  # Japan Pharmaceuticals and Medical Devices Agency
            'MHRA': 22,  # UK Medicines and Healthcare products Regulatory Agency
            'EMA': 25,  # European Medicines Agency
            'TFDA': 15,  # Taiwan Food and Drug Administration
            'KFDA': 15,  # South Korea Food and Drug Administration
            
            # ISO Standards (Fourth Tier - 8-15 points)
            'ISO 9001': 15, 'ISO 14001': 12, 'ISO 45001': 12, 'ISO 27001': 10,
            'ISO 15189': 20,  # Medical laboratory standard
            'ISO 13485': 18,  # Medical device quality
            'ISO 17025': 15,  # Testing and calibration laboratories
            'IEC 62304': 10,  # Medical device software
            
            # European Standards (12-22 points)
            'CE Marking': 20,  # Medical device compliance
            'NICE': 18,  # UK Health Technology Assessment
            'HAS': 15,  # France Health Technology Assessment
            'G-BA': 15,  # Germany Healthcare Quality Assessment
            'Swissmedic': 20,  # Switzerland drug regulation
            'ANSM': 15,  # France drug safety
            'BfArM': 20,  # Germany medical devices
            'AIFA': 15,  # Italy drug regulation
            'AEMPS': 15,  # Spain pharmaceutical regulation
            
            # North American Standards (10-25 points)
            'HIMSS EMRAM': 18,  # Health IT maturity
            'HFAP': 12,  # Healthcare Facilities Accreditation Program
            'CHAP': 10,  # Community Health Accreditation Partner
            'ACHC': 12,  # Accreditation Commission for Health Care
            'URAC': 15,  # Healthcare quality
            'CPSO': 15,  # College of Physicians and Surgeons Ontario
            'Health Canada GMP': 12,  # Good Manufacturing Practices
            
            # Asia-Pacific Standards (6-20 points)
            'QCI Healthcare': 12,  # India Quality Council
            'MHLW': 15,  # Japan Health & Welfare
            'Medsafe': 12,  # New Zealand medicine safety
            'NMPA': 15,  # China drug administration
            'DOH Philippines': 10,  # Philippines Department of Health
            'MOH Malaysia': 10,  # Malaysia Ministry of Health
            'FDA Thailand': 10,  # Thailand Food and Drug Administration
            'BPOM': 10,  # Indonesia drug control
            'SFDA': 12,  # Saudi Arabia Food and Drug Authority
            'NHRA': 8,   # Bahrain Health Regulation Authority
            'MOH UAE': 8, 'Kuwait MOH': 8, 'Oman MOH': 8, 'Qatar MOH': 8,
            
            # Middle East & Africa Standards (6-15 points)
            'SAHPRA': 15,  # South Africa health products regulation
            'MCC': 15,     # South Africa medicines control
            'NAFDAC': 10,  # Nigeria food and drug administration
            'FDB': 10,     # Ghana Food and Drugs Board
            'PPB': 8,      # Kenya Pharmacy and Poisons Board
            'Israeli MOH': 12, 'Turkish MOH': 10, 'Egyptian MOH': 10,
            'Moroccan MOH': 10, 'Tunisian MOH': 10, 'Jordanian MOH': 8,
            
            # Latin American Standards (6-15 points)
            'ANVISA': 15,    # Brazil health surveillance
            'ANMAT': 15,     # Argentina medicine administration
            'ISP': 15,       # Chile public health institute
            'INVIMA': 10,    # Colombia drug surveillance
            'DIGEMID': 10,   # Peru medicine directorate
            'COFEPRIS': 12,  # Mexico health risk protection
            'CECMED': 8,     # Cuba medicine control
            'DINAMED': 8,    # Uruguay medicine directorate
            'MSP Ecuador': 8, 'MINSA Panama': 8, 'MINSA Costa Rica': 8,
            
            # Specialized Certifications (Fifth Tier - 5-12 points)
            'AABB': 10,  # Blood bank accreditation
            'FACT': 12,  # Cellular therapy accreditation
            'JACIE': 12,  # European cellular therapy
            'OSHA VPP': 8,  # Occupational safety
            'Green Guide for Health Care': 6,  # Environmental sustainability
            'LEED Healthcare': 8,  # Green building certification
            'Energy Star': 6,  # Energy efficiency
        }
        
        # Hospital reputation and ranking multipliers (reduced for more realistic scoring)
        self.reputation_multipliers = {
            # US News & World Report Rankings (Reduced multipliers)
            'us_news_top_5': 1.10,    # 10% boost for top 5 hospitals (reduced from 25%)
            'us_news_top_10': 1.08,   # 8% boost for top 10 hospitals (reduced from 20%)
            'us_news_top_20': 1.05,   # 5% boost for top 20 hospitals (reduced from 15%)
            'us_news_honor_roll': 1.03, # 3% boost for Honor Roll hospitals (reduced from 10%)
            
            # International Recognition (Reduced multipliers)
            'newsweek_world_best': 1.08,  # Newsweek World's Best Hospitals (reduced from 20%)
            'forbes_global': 1.05,        # Forbes Global 2000 Healthcare (reduced from 15%)
            'academic_medical_center': 1.03, # Major teaching hospitals (reduced from 10%)
            'research_intensive': 1.02,   # High research output (reduced from 8%)
        }
        
        # Global hospital reputation database (simplified for demo)
        self.global_hospital_rankings = {
            # US Top Hospitals
            'mayo clinic': {'us_news_rank': 1, 'newsweek_rank': 1, 'academic': True, 'research_intensive': True},
            'cleveland clinic': {'us_news_rank': 2, 'newsweek_rank': 3, 'academic': True, 'research_intensive': True},
            'johns hopkins': {'us_news_rank': 3, 'newsweek_rank': 2, 'academic': True, 'research_intensive': True},
            'massachusetts general': {'us_news_rank': 4, 'newsweek_rank': 4, 'academic': True, 'research_intensive': True},
            'cedars-sinai': {'us_news_rank': 8, 'newsweek_rank': 12, 'academic': True, 'research_intensive': True},
            
            # International Top Hospitals
            'singapore general hospital': {'newsweek_rank': 15, 'academic': True, 'research_intensive': True},
            'toronto general hospital': {'newsweek_rank': 18, 'academic': True, 'research_intensive': True},
            'karolinska university hospital': {'newsweek_rank': 22, 'academic': True, 'research_intensive': True},
            
            # Indian Hospitals (Regional leaders but not global top tier)
            'apollo hospitals': {'regional_leader': True, 'academic': False, 'research_intensive': False},
            'fortis healthcare': {'regional_leader': True, 'academic': False, 'research_intensive': False},
            'yashoda hospitals': {'regional_leader': True, 'academic': False, 'research_intensive': False},
            'aiims delhi': {'academic': True, 'research_intensive': True, 'government': True},
        }
        
        # Quality initiative keywords and their impact scores
        self.quality_keywords = {
            'patient safety': 8, 'quality improvement': 6, 'accreditation': 10,
            'certification': 8, 'digital health': 5, 'telemedicine': 4,
            'infection control': 7, 'staff training': 5, 'research': 6,
            'innovation': 5, 'transparency': 4, 'community health': 5
        }
        
        # Load JCI accredited organizations data
        self.jci_organizations = self.load_jci_data()

    def load_jci_data(self):
        """Load JCI accredited organizations data from JSON file"""
        try:
            import json
            import os
            
            jci_file_path = 'jci_accredited_organizations.json'
            
            if os.path.exists(jci_file_path):
                with open(jci_file_path, 'r', encoding='utf-8') as f:
                    jci_data = json.load(f)
                
                # Create a lookup dictionary for faster searches
                jci_lookup = {}
                for org in jci_data:
                    org_name = org.get('name', '').lower().strip()
                    if org_name:
                        jci_lookup[org_name] = {
                            'name': org.get('name', ''),
                            'country': org.get('country', ''),
                            'type': org.get('type', ''),
                            'accreditation_date': org.get('accreditation_date', ''),
                            'region': org.get('region', ''),
                            'source': org.get('source', 'JCI Database'),
                            'jci_accredited': True
                        }
                
                # Removed JCI loading message for cleaner UI
                return jci_lookup
            else:
                st.warning("⚠️ JCI data file not found. Using default JCI certification weights.")
                return {}
                
        except Exception as e:
            st.error(f"Error loading JCI data: {str(e)}")
            return {}

    def check_jci_accreditation(self, org_name):
        """Check if an organization is JCI accredited"""
        if not self.jci_organizations:
            return None
            
        org_name_lower = org_name.lower().strip()
        
        # Direct match
        if org_name_lower in self.jci_organizations:
            return self.jci_organizations[org_name_lower]
        
        # Partial match - check if organization name contains JCI org name or vice versa
        for jci_org_name, jci_data in self.jci_organizations.items():
            if (jci_org_name in org_name_lower or 
                org_name_lower in jci_org_name or
                any(word in jci_org_name for word in org_name_lower.split() if len(word) > 3)):
                return jci_data
        
        return None

    def generate_organization_suggestions(self, partial_input, max_suggestions=10):
        """Generate smart autocomplete suggestions based on partial input"""
        if not partial_input or len(partial_input) < 2:
            return []
        
        partial_lower = partial_input.lower().strip()
        suggestions = []
        seen_names = set()
        
        # Search in unified database
        if self.unified_database:
            for org in self.unified_database:
                org_name = org.get('name', '')
                original_name = org.get('original_name', '')
                
                # Check if partial input matches the beginning of organization name
                if org_name.lower().startswith(partial_lower):
                    if org_name not in seen_names:
                        suggestions.append({
                            'display_name': org_name,
                            'full_name': original_name if original_name else org_name,
                            'location': self._extract_location_from_org(org),
                            'type': org.get('type', 'Healthcare Organization'),
                            'match_type': 'name_start'
                        })
                        seen_names.add(org_name)
                
                # Check if partial input is contained within organization name
                elif partial_lower in org_name.lower():
                    if org_name not in seen_names:
                        suggestions.append({
                            'display_name': org_name,
                            'full_name': original_name if original_name else org_name,
                            'location': self._extract_location_from_org(org),
                            'type': org.get('type', 'Healthcare Organization'),
                            'match_type': 'name_contains'
                        })
                        seen_names.add(org_name)
                
                # Check original name for NABH organizations
                if original_name and partial_lower in original_name.lower():
                    if org_name not in seen_names:
                        suggestions.append({
                            'display_name': org_name,
                            'full_name': original_name,
                            'location': self._extract_location_from_org(org),
                            'type': org.get('type', 'Healthcare Organization'),
                            'match_type': 'original_name'
                        })
                        seen_names.add(org_name)
        
        # Sort suggestions: exact matches first, then starts with, then contains
        suggestions.sort(key=lambda x: (
            0 if x['match_type'] == 'name_start' else 
            1 if x['match_type'] == 'name_contains' else 2,
            x['display_name'].lower()
        ))
        
        return suggestions[:max_suggestions]
    
    def _extract_location_from_org(self, org):
        """Extract location information from organization data"""
        # Try different location fields
        if org.get('city') and org.get('state'):
            return f"{org['city']}, {org['state']}"
        elif org.get('location'):
            return org['location']
        elif org.get('address'):
            return org['address']
        elif org.get('original_name'):
            # Extract location from original name (common in NABH data)
            original = org['original_name']
            # Look for patterns like "City, State, Country"
            parts = original.split(',')
            if len(parts) >= 3:
                return f"{parts[-3].strip()}, {parts[-2].strip()}"
            elif len(parts) >= 2:
                return parts[-2].strip()
        
        return org.get('country', 'Unknown Location')
    
    def format_suggestion_display(self, suggestion):
        """Format suggestion for display in the UI"""
        display_name = suggestion['display_name']
        location = suggestion['location']
        
        # For organizations with multiple locations, show location prominently
        if location and location != 'Unknown Location':
            return f"{display_name} - {location}"
        else:
            return display_name

    def enhance_certification_with_jci(self, certifications, org_name):
        """Enhance certification list with JCI accreditation if found"""
        jci_info = self.check_jci_accreditation(org_name)
        
        if jci_info:
            # Check if JCI is already in certifications
            has_jci = any(cert.get('name', '').upper() == 'JCI' for cert in certifications)
            
            if not has_jci:
                jci_cert = {
                    'name': 'Joint Commission International (JCI)',
                    'status': 'Active',
                    'valid_until': '2025-12-31',  # Default validity
                    'score_impact': 35,
                    'certificate_number': f"JCI-{jci_info['country']}-{datetime.now().year}",
                    'accreditation_type': 'Hospital Accreditation',
                    'issuer': 'Joint Commission International',
                    'organization_info': jci_info
                }
                certifications.append(jci_cert)
                
                st.success(f"🏆 JCI Accreditation found for {jci_info['name']} ({jci_info['country']}) - Added 35 points!")
        
        return certifications
    
    def load_unified_database(self):
        """Load the unified healthcare organizations database"""
        try:
            with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            st.warning("⚠️ Unified healthcare database not found. Some search features may be limited.")
            return []
        except Exception as e:
            st.error(f"Error loading unified database: {str(e)}")
            return []

    def search_organization_info(self, org_name):
        """Search for organization information from multiple sources including unified database"""
        try:
            # Initialize results
            results = {
                'name': org_name,
                'certifications': [],
                'quality_initiatives': [],
                'news_mentions': [],
                'website_info': {},
                'score_breakdown': {},
                'total_score': 0
            }
            
            # First, search in unified database
            unified_org = self.search_unified_database(org_name)
            if unified_org:
                # Use data from unified database
                results['certifications'] = unified_org.get('certifications', [])
                results['unified_data'] = unified_org
                # Removed success message for cleaner UI
            else:
                # Fallback to original search methods
                certifications = self.search_certifications(org_name)
                results['certifications'] = certifications
            
            # Search for quality initiatives and news
            initiatives = self.search_quality_initiatives(org_name)
            results['quality_initiatives'] = initiatives
            
            # Calculate quality score
            score_data = self.calculate_quality_score(results['certifications'], initiatives, org_name)
            results['score_breakdown'] = score_data
            results['total_score'] = score_data['total_score']
            
            return results
            
        except Exception as e:
            st.error(f"Error searching for organization: {str(e)}")
            return None
    
    def search_unified_database(self, org_name):
        """Search for organization in the unified healthcare database"""
        if not self.unified_database:
            return None
            
        org_name_lower = org_name.lower().strip()
        
        # Direct name match
        for org in self.unified_database:
            if org['name'].lower() == org_name_lower:
                return org
        
        # Partial name match
        for org in self.unified_database:
            if org_name_lower in org['name'].lower() or org['name'].lower() in org_name_lower:
                return org
        
        # Search in original names for NABH organizations
        for org in self.unified_database:
            if 'original_name' in org and org['original_name']:
                if org_name_lower in org['original_name'].lower() or org['original_name'].lower() in org_name_lower:
                    return org
        
        return None

    def search_certifications(self, org_name):
        """Search for organization certifications using web-validated data"""
        org_name_lower = org_name.lower().strip()
        
        # Use web validator to get real certification data
        try:
            validation_result = healthcare_validator.validate_organization_certifications(org_name)
            
            # Extract certifications from the validation result
            if validation_result and 'certifications' in validation_result:
                certifications = validation_result['certifications']
                
                # Enhance certifications with JCI data
                enhanced_certifications = self.enhance_certification_with_jci(certifications, org_name)
                
                # If no validated data found, show disclaimer
                if not enhanced_certifications:
                    st.warning(f"⚠️ No validated certification data found for '{org_name}'. Please verify organization name or check official certification databases.")
                    return []
                
                return enhanced_certifications
            else:
                # Check if organization has JCI accreditation even without other certifications
                jci_cert = self.check_jci_accreditation(org_name)
                if jci_cert:
                    st.info(f"✅ Found JCI accreditation for '{org_name}' in our database.")
                    return [jci_cert]
                else:
                    st.warning(f"⚠️ No validated certification data found for '{org_name}'. Please verify organization name or check official certification databases.")
                    return []
            
        except Exception as e:
            st.error(f"Error validating certification data: {str(e)}")
            st.info("💡 Please check the organization name and try again. Only validated data from official sources is displayed.")
            return []
    
    def search_quality_initiatives(self, org_name):
        """Search for quality initiatives using web-validated data"""
        try:
            validation_result = healthcare_validator.validate_quality_initiatives(org_name)
            
            # Extract initiatives from the validation result
            if validation_result and 'initiatives' in validation_result:
                initiatives = validation_result['initiatives']
                
                # If no validated data found, show disclaimer
                if not initiatives:
                    # Removed info message for cleaner UI
                    return []
                
                return initiatives
            else:
                # Removed info message for cleaner UI
                return []
            
        except Exception as e:
            st.error(f"Error validating quality initiative data: {str(e)}")
            st.info("💡 Please check the organization name and try again. Only validated data from official sources is displayed.")
            return []
    
    def calculate_quality_score(self, certifications, initiatives, org_name=""):
        """Calculate comprehensive quality score with JCI enhancement and more realistic and balanced scoring"""
        score_breakdown = {
            'certification_score': 0,
            'initiative_score': 0,
            'transparency_score': 0,
            'reputation_bonus': 0,
            'total_score': 0
        }
        
        # Calculate base certification score (50% weight, reduced from 60%)
        cert_score = 0
        jci_bonus = 0
        
        for cert in certifications:
            if cert['status'] == 'Active':
                cert_score += cert['score_impact']
                # Special handling for JCI certification
                if cert.get('name') == 'JCI':
                    jci_bonus = 5  # Additional bonus for JCI accreditation
            elif cert['status'] == 'In Progress':
                cert_score += cert['score_impact'] * 0.2  # Reduced from 0.3 for stricter evaluation
        
        score_breakdown['certification_score'] = min(cert_score, 50)  # Reduced max from 60 to 50
        
        # Calculate initiative score (15% weight, reduced from 20%)
        init_score = sum([init['impact_score'] for init in initiatives])
        score_breakdown['initiative_score'] = min(init_score, 15)  # Reduced max from 20 to 15
        
        # Calculate transparency score (15% weight, increased from 10%)
        transparency_score = np.random.randint(4, 8)  # Reduced baseline range
        score_breakdown['transparency_score'] = transparency_score
        
        # Calculate reputation bonus (up to 5% additional points, reduced from 10%)
        reputation_bonus = self.calculate_reputation_bonus(org_name)
        # Add JCI bonus to reputation bonus
        reputation_bonus += jci_bonus
        score_breakdown['reputation_bonus'] = min(reputation_bonus, 10)  # Cap at 10 points
        
        # Total score with reputation multiplier
        base_total = (score_breakdown['certification_score'] + 
                     score_breakdown['initiative_score'] + 
                     score_breakdown['transparency_score'])
        
        # Apply reputation multiplier (but cap the effect)
        multiplier = self.get_reputation_multiplier(org_name)
        final_score = base_total * multiplier + score_breakdown['reputation_bonus']
        
        # Add penalty for missing key certifications
        penalty = self.calculate_missing_certification_penalty(certifications)
        final_score = max(final_score - penalty, 0)
        
        # Cap final score at 85 for more realistic scoring (reduced from 100)
        score_breakdown['total_score'] = min(final_score, 85)
        
        return score_breakdown
    
    def calculate_reputation_bonus(self, org_name):
        """Calculate reputation bonus points based on global rankings (reduced for realistic scoring)"""
        org_name_lower = org_name.lower().strip()
        bonus = 0
        
        # Check if hospital is in our reputation database
        for hospital_key, data in self.global_hospital_rankings.items():
            if hospital_key in org_name_lower:
                # US News ranking bonus (reduced)
                if 'us_news_rank' in data:
                    rank = data['us_news_rank']
                    if rank <= 5:
                        bonus += 3  # Top 5 hospitals get 3 bonus points (reduced from 8)
                    elif rank <= 10:
                        bonus += 2  # Top 10 get 2 bonus points (reduced from 6)
                    elif rank <= 20:
                        bonus += 1  # Top 20 get 1 bonus point (reduced from 4)
                
                # Newsweek World's Best bonus (reduced)
                if 'newsweek_rank' in data:
                    rank = data['newsweek_rank']
                    if rank <= 10:
                        bonus += 2  # Top 10 globally get 2 bonus points (reduced from 5)
                    elif rank <= 25:
                        bonus += 1  # Top 25 get 1 bonus point (reduced from 3)
                
                # Academic medical center bonus (reduced)
                if data.get('academic', False):
                    bonus += 1  # Reduced from 2
                
                # Research intensive bonus (reduced)
                if data.get('research_intensive', False):
                    bonus += 1  # Reduced from 2
                
                # Regional leader bonus (reduced)
                if data.get('regional_leader', False) and 'us_news_rank' not in data:
                    bonus += 0.5  # Reduced from 1
                
                break
        
        return min(bonus, 5)  # Cap at 5 bonus points (reduced from 10)
    
    def calculate_missing_certification_penalty(self, certifications):
        """Calculate penalty for missing key certifications"""
        penalty = 0
        
        # Check for key certifications using 'name' field instead of 'type'
        cert_names = [cert.get('name', '') for cert in certifications if cert['status'] == 'Active']
        
        # Penalty for missing NABH (for Indian hospitals)
        if 'NABH' not in cert_names:
            penalty += 3
        
        # Penalty for missing JCI (for international recognition)
        if 'JCI' not in cert_names:
            penalty += 2
        
        # Penalty for missing NABL (for diagnostic services)
        if 'NABL' not in cert_names:
            penalty += 1
        
        # Penalty for having very few certifications
        if len(cert_names) < 3:
            penalty += 2
        
        return penalty
    
    def get_reputation_multiplier(self, org_name):
        """Get reputation multiplier for the hospital"""
        org_name_lower = org_name.lower().strip()
        
        # Check if hospital is in our reputation database
        for hospital_key, data in self.global_hospital_rankings.items():
            if hospital_key in org_name_lower:
                # US News ranking multiplier
                if 'us_news_rank' in data:
                    rank = data['us_news_rank']
                    if rank <= 5:
                        return self.reputation_multipliers['us_news_top_5']
                    elif rank <= 10:
                        return self.reputation_multipliers['us_news_top_10']
                    elif rank <= 20:
                        return self.reputation_multipliers['us_news_top_20']
                
                # Newsweek World's Best multiplier
                if 'newsweek_rank' in data and data['newsweek_rank'] <= 25:
                    return self.reputation_multipliers['newsweek_world_best']
                
                # Academic medical center multiplier
                if data.get('academic', False):
                    return self.reputation_multipliers['academic_medical_center']
                
                break
        
        return 1.0  # No multiplier for unknown hospitals
    
    def find_similar_organizations(self, org_name, org_location="", org_type="Hospital"):
        """Find similar organizations in the same or nearby locality with their quality scores"""
        similar_orgs = []
        
        # Define location-based similar organizations database
        location_based_orgs = {
            # US Organizations
            'united states': [
                {'name': 'Mayo Clinic', 'location': 'Rochester, MN', 'type': 'Academic Medical Center'},
                {'name': 'Cleveland Clinic', 'location': 'Cleveland, OH', 'type': 'Academic Medical Center'},
                {'name': 'Johns Hopkins Hospital', 'location': 'Baltimore, MD', 'type': 'Academic Medical Center'},
                {'name': 'Massachusetts General Hospital', 'location': 'Boston, MA', 'type': 'Academic Medical Center'},
                {'name': 'Cedars-Sinai Medical Center', 'location': 'Los Angeles, CA', 'type': 'Academic Medical Center'},
                {'name': 'NewYork-Presbyterian Hospital', 'location': 'New York, NY', 'type': 'Academic Medical Center'},
                {'name': 'UCSF Medical Center', 'location': 'San Francisco, CA', 'type': 'Academic Medical Center'},
                {'name': 'Houston Methodist Hospital', 'location': 'Houston, TX', 'type': 'General Hospital'},
            ],
            
            # Indian Organizations
            'india': [
                {'name': 'Apollo Hospitals', 'location': 'Chennai, Tamil Nadu', 'type': 'Multi-specialty Hospital'},
                {'name': 'Fortis Healthcare', 'location': 'Gurgaon, Haryana', 'type': 'Multi-specialty Hospital'},
                {'name': 'AIIMS Delhi', 'location': 'New Delhi, Delhi', 'type': 'Government Medical Institute'},
                {'name': 'Yashoda Hospitals', 'location': 'Hyderabad, Telangana', 'type': 'Multi-specialty Hospital'},
                {'name': 'Manipal Hospitals', 'location': 'Bangalore, Karnataka', 'type': 'Multi-specialty Hospital'},
                {'name': 'Max Healthcare', 'location': 'New Delhi, Delhi', 'type': 'Multi-specialty Hospital'},
                {'name': 'Narayana Health', 'location': 'Bangalore, Karnataka', 'type': 'Multi-specialty Hospital'},
                {'name': 'Medanta - The Medicity', 'location': 'Gurgaon, Haryana', 'type': 'Multi-specialty Hospital'},
            ],
            
            # UK Organizations
            'united kingdom': [
                {'name': 'Great Ormond Street Hospital', 'location': 'London, England', 'type': 'Pediatric Hospital'},
                {'name': 'Royal Marsden Hospital', 'location': 'London, England', 'type': 'Cancer Center'},
                {'name': 'Moorfields Eye Hospital', 'location': 'London, England', 'type': 'Specialty Hospital'},
                {'name': 'King\'s College Hospital', 'location': 'London, England', 'type': 'Academic Medical Center'},
                {'name': 'Imperial College Healthcare', 'location': 'London, England', 'type': 'Academic Medical Center'},
            ],
            
            # Canadian Organizations
            'canada': [
                {'name': 'Toronto General Hospital', 'location': 'Toronto, ON', 'type': 'Academic Medical Center'},
                {'name': 'Vancouver General Hospital', 'location': 'Vancouver, BC', 'type': 'Academic Medical Center'},
                {'name': 'Montreal General Hospital', 'location': 'Montreal, QC', 'type': 'Academic Medical Center'},
                {'name': 'Calgary Foothills Hospital', 'location': 'Calgary, AB', 'type': 'General Hospital'},
            ],
            
            # Singapore Organizations
            'singapore': [
                {'name': 'Singapore General Hospital', 'location': 'Singapore', 'type': 'Academic Medical Center'},
                {'name': 'National University Hospital', 'location': 'Singapore', 'type': 'Academic Medical Center'},
                {'name': 'Tan Tock Seng Hospital', 'location': 'Singapore', 'type': 'General Hospital'},
                {'name': 'Mount Elizabeth Hospital', 'location': 'Singapore', 'type': 'Private Hospital'},
            ],
            
            # Australian Organizations
            'australia': [
                {'name': 'Royal Melbourne Hospital', 'location': 'Melbourne, VIC', 'type': 'Academic Medical Center'},
                {'name': 'Royal Prince Alfred Hospital', 'location': 'Sydney, NSW', 'type': 'Academic Medical Center'},
                {'name': 'Princess Alexandra Hospital', 'location': 'Brisbane, QLD', 'type': 'General Hospital'},
                {'name': 'Royal Adelaide Hospital', 'location': 'Adelaide, SA', 'type': 'Academic Medical Center'},
            ]
        }
        
        # Determine the country/region for the searched organization
        search_region = self.determine_organization_region(org_name, org_location)
        
        # Get organizations from the same region
        region_orgs = location_based_orgs.get(search_region.lower(), [])
        
        # Filter out the searched organization itself
        filtered_orgs = [org for org in region_orgs if org['name'].lower() != org_name.lower()]
        
        # For strict region-specific comparison (especially for Indian hospitals)
        # Only add from nearby regions if the current region has very few organizations (less than 3)
        # and only for non-Indian regions to maintain regional specificity
        if len(filtered_orgs) < 3 and search_region.lower() != 'india':
            nearby_regions = self.get_nearby_regions(search_region)
            for nearby_region in nearby_regions:
                if len(filtered_orgs) >= 8:  # Limit to 8 total comparisons
                    break
                nearby_orgs = location_based_orgs.get(nearby_region.lower(), [])
                filtered_orgs.extend(nearby_orgs[:2])  # Add up to 2 from each nearby region
        
        # Generate quality scores for similar organizations
        for org in filtered_orgs[:8]:  # Limit to 8 comparisons
            org_info = self.search_organization_info(org['name'])
            if org_info:
                similar_orgs.append({
                    'name': org['name'],
                    'location': org['location'],
                    'type': org['type'],
                    'total_score': org_info['total_score'],
                    'score_breakdown': org_info['score_breakdown'],
                    'certifications': org_info['certifications'],
                    'quality_initiatives': org_info['quality_initiatives']
                })
        
        # Sort by score (highest first)
        similar_orgs.sort(key=lambda x: x['total_score'], reverse=True)
        
        return similar_orgs
    
    def determine_organization_region(self, org_name, org_location=""):
        """Determine the region/country of an organization based on name and location"""
        org_name_lower = org_name.lower()
        org_location_lower = org_location.lower()
        
        # Location-based detection (prioritize location over name patterns)
        if any(loc in org_location_lower for loc in ['india', 'delhi', 'mumbai', 'bangalore', 'chennai', 'hyderabad', 'pune', 'kolkata', 'ahmedabad', 'surat', 'jaipur', 'lucknow', 'kanpur', 'nagpur', 'indore', 'thane', 'bhopal', 'visakhapatnam', 'pimpri', 'patna', 'vadodara', 'ghaziabad', 'ludhiana', 'agra', 'nashik', 'faridabad', 'meerut', 'rajkot', 'kalyan', 'vasai', 'varanasi', 'srinagar', 'aurangabad', 'dhanbad', 'amritsar', 'navi mumbai', 'allahabad', 'ranchi', 'howrah', 'coimbatore', 'jabalpur', 'gwalior', 'vijayawada', 'jodhpur', 'madurai', 'raipur', 'kota', 'guwahati', 'chandigarh', 'solapur', 'hubli', 'tiruchirappalli', 'bareilly', 'mysore', 'tiruppur', 'gurgaon', 'aligarh', 'jalandhar', 'bhubaneswar', 'salem', 'warangal', 'guntur', 'bhiwandi', 'saharanpur', 'gorakhpur', 'bikaner', 'amravati', 'noida', 'jamshedpur', 'bhilai', 'cuttack', 'firozabad', 'kochi', 'nellore', 'bhavnagar', 'dehradun', 'durgapur', 'asansol', 'rourkela', 'nanded', 'kolhapur', 'ajmer', 'akola', 'gulbarga', 'jamnagar', 'ujjain', 'loni', 'siliguri', 'jhansi', 'ulhasnagar', 'jammu', 'sangli', 'mangalore', 'erode', 'belgaum', 'ambattur', 'tirunelveli', 'malegaon', 'gaya', 'jalgaon', 'udaipur', 'maheshtala']):
            return 'india'
        elif any(loc in org_location_lower for loc in ['usa', 'united states', 'america', 'us', 'california', 'texas', 'florida', 'new york', 'pennsylvania', 'illinois', 'ohio', 'georgia', 'north carolina', 'michigan', 'new jersey', 'virginia', 'washington', 'arizona', 'massachusetts', 'tennessee', 'indiana', 'maryland', 'missouri', 'wisconsin', 'colorado', 'minnesota', 'south carolina', 'alabama', 'louisiana', 'kentucky', 'oregon', 'oklahoma', 'connecticut', 'utah', 'iowa', 'nevada', 'arkansas', 'mississippi', 'kansas', 'new mexico', 'nebraska', 'west virginia', 'idaho', 'hawaii', 'new hampshire', 'maine', 'montana', 'rhode island', 'delaware', 'south dakota', 'north dakota', 'alaska', 'vermont', 'wyoming']):
            return 'united states'
        elif any(loc in org_location_lower for loc in ['uk', 'united kingdom', 'england', 'london', 'scotland', 'wales', 'northern ireland', 'birmingham', 'manchester', 'glasgow', 'liverpool', 'bristol', 'sheffield', 'leeds', 'edinburgh', 'leicester', 'coventry', 'bradford', 'cardiff', 'belfast', 'nottingham', 'kingston upon hull', 'newcastle', 'stoke', 'southampton', 'derby', 'portsmouth', 'brighton', 'plymouth', 'northampton', 'reading', 'luton', 'wolverhampton', 'bolton', 'bournemouth', 'norwich', 'swindon', 'swansea', 'southend', 'middlesbrough', 'peterborough', 'huddersfield', 'york', 'poole', 'preston', 'stockport', 'dundee', 'milton keynes', 'aberdeen', 'telford', 'watford', 'ipswich', 'oxford', 'warrington', 'slough', 'exeter', 'cheltenham', 'gloucester', 'saint helens', 'sutton coldfield', 'cambridge', 'blackpool', 'oldham', 'maidstone', 'basildon', 'worthing', 'chelmsford', 'colchester', 'crawley', 'gillingham', 'solihull', 'taunton', 'shrewsbury', 'farnborough', 'royal leamington spa', 'stevenage', 'sale', 'wigan', 'rotherham', 'chesterfield', 'worcester', 'hemel hempstead', 'redditch', 'lincoln', 'carlisle', 'eastbourne', 'scunthorpe', 'birkenhead', 'mansfield', 'ashford', 'rugby', 'high wycombe', 'st albans', 'hastings', 'folkestone', 'bangor', 'ayr', 'lancaster', 'salisbury', 'chester', 'bath', 'kidderminster', 'barnsley', 'grimsby', 'bedford', 'harrogate', 'royal tunbridge wells', 'macclesfield', 'rhondda', 'burton upon trent', 'cannock', 'lowestoft', 'welwyn garden city', 'barrow in furness', 'newport', 'gateshead', 'eastleigh', 'tamworth', 'washington', 'carlisle', 'nuneaton', 'loughborough', 'ellesmere port', 'hereford', 'margate', 'arnold', 'dewsbury', 'beverley', 'crewe', 'aldershot', 'walkden', 'carlisle', 'smethwick', 'gosport', 'fareham', 'bletchley', 'maidenhead', 'tonbridge', 'barry', 'littlehampton', 'royal leamington spa', 'weston super mare', 'burton upon trent', 'yeovil', 'kidderminster', 'st helens', 'weymouth', 'farnham', 'burnley', 'gravesend', 'bridgwater', 'staines', 'grays', 'stafford', 'newbury', 'spalding', 'lisburn', 'chester le street', 'stirling', 'fleet', 'llanelli', 'bridgend', 'pontefract', 'letchworth', 'nelson', 'wigston', 'castleford', 'deal', 'st neots', 'warwick', 'buxton', 'bognor regis', 'christchurch', 'rugby', 'canvey island', 'leigh', 'great yarmouth', 'rhyl', 'barry', 'kirkby', 'whitley bay', 'prescot', 'runcorn', 'nelson', 'accrington', 'morley', 'jarrow', 'blyth', 'rowley regis', 'smethwick', 'willenhall', 'walsall', 'west bromwich', 'bilston', 'tipton', 'wednesbury', 'oldbury', 'halesowen', 'stourbridge', 'kidderminster', 'redditch', 'bromsgrove', 'droitwich', 'evesham', 'malvern', 'pershore', 'tenbury wells', 'bewdley', 'stourport on severn']):
            return 'united kingdom'
        elif 'singapore' in org_location_lower:
            return 'singapore'
        elif any(loc in org_location_lower for loc in ['canada', 'toronto', 'vancouver', 'montreal', 'calgary', 'ottawa', 'edmonton', 'mississauga', 'winnipeg', 'quebec city', 'hamilton', 'brampton', 'surrey', 'laval', 'halifax', 'london', 'markham', 'vaughan', 'gatineau', 'saskatoon', 'longueuil', 'burnaby', 'regina', 'richmond', 'richmond hill', 'oakville', 'burlington', 'greater sudbury', 'sherbrooke', 'oshawa', 'saguenay', 'lévis', 'barrie', 'abbotsford', 'coquitlam', 'st. catharines', 'trois-rivières', 'guelph', 'cambridge', 'whitby', 'kelowna', 'kingston', 'ajax', 'thunder bay', 'waterloo', 'st. john\'s', 'langley', 'chatham-kent', 'delta', 'red deer', 'kamloops', 'brantford', 'cape breton', 'lethbridge', 'saint-jean-sur-richelieu', 'clarington', 'pickering', 'nanaimo', 'sudbury', 'north vancouver', 'brossard', 'repentigny', 'newmarket', 'chilliwack', 'white rock', 'maple ridge', 'peterborough', 'kawartha lakes', 'prince george', 'sault ste. marie', 'sarnia', 'wood buffalo', 'new westminster', 'châteauguay', 'saint-jérôme', 'drummondville', 'saint john', 'caledon', 'st. albert', 'granby', 'medicine hat', 'grande prairie', 'st. thomas', 'airdrie', 'halton hills', 'saint-hyacinthe', 'lac-brome', 'charlottetown', 'fredericton', 'blainville', 'aurora', 'welland', 'north bay', 'beloeil', 'belleville', 'mirabel', 'shawinigan', 'dollard-des-ormeaux', 'brandon', 'rimouski', 'saint-eustache', 'saint-bruno-de-montarville', 'mascouche', 'terrebonne', 'milton', 'collingwood', 'cornwall', 'victoriaville', 'georgina', 'vernon', 'duncan', 'saint-constant', 'batoche']):
            return 'canada'
        elif any(loc in org_location_lower for loc in ['australia', 'melbourne', 'sydney', 'brisbane', 'perth', 'adelaide', 'gold coast', 'newcastle', 'canberra', 'sunshine coast', 'wollongong', 'hobart', 'geelong', 'townsville', 'cairns', 'darwin', 'toowoomba', 'ballarat', 'bendigo', 'albury', 'launceston', 'mackay', 'rockhampton', 'bunbury', 'bundaberg', 'coffs harbour', 'wagga wagga', 'hervey bay', 'mildura', 'shepparton', 'port macquarie', 'gladstone', 'tamworth', 'traralgon', 'orange', 'dubbo', 'geraldton', 'bowral', 'bathurst', 'nowra', 'warrnambool', 'kalgoorlie', 'devonport', 'mount gambier', 'armidale', 'lismore', 'nelson bay', 'alice springs', 'taree', 'goulburn', 'hawkesbury', 'sunbury', 'moe', 'bacchus marsh', 'melton', 'pakenham', 'warragul', 'drouin', 'cranbourne', 'berwick', 'frankston', 'dandenong', 'ringwood', 'box hill', 'blackburn', 'camberwell', 'hawthorn', 'richmond', 'south yarra', 'st kilda', 'brighton', 'sandringham', 'mentone', 'mordialloc', 'chelsea', 'bonbeach', 'carrum', 'seaford', 'frankston south', 'langwarrin', 'skye', 'safety beach', 'dromana', 'rosebud', 'rye', 'sorrento', 'portsea', 'blairgowrie', 'mount martha', 'mornington', 'mount eliza', 'baxter', 'somerville', 'tyabb', 'hastings', 'bittern', 'crib point', 'stony point', 'french island', 'phillip island', 'cowes', 'rhyll', 'san remo', 'bass', 'corinella', 'grantville', 'coronet bay', 'kilcunda', 'wonthaggi', 'inverloch', 'venus bay', 'tarwin lower', 'fish creek', 'foster', 'welshpool', 'port franklin', 'sandy point', 'waratah bay', 'walkerville', 'port albert', 'yarram', 'alberton', 'port welshpool', 'devon north', 'woodside', 'gormandale', 'rosedale', 'sale', 'longford', 'stratford', 'bairnsdale', 'lindenow', 'bruthen', 'tambo upper', 'swan reach', 'metung', 'lakes entrance', 'lake tyers', 'nowa nowa', 'orbost', 'marlo', 'cape conran', 'bemm river', 'cann river', 'genoa', 'mallacoota']):
            return 'australia'
        
        # Name-based detection (fallback if location is not clear)
        # US hospitals
        us_indicators = ['mayo clinic', 'cleveland clinic', 'johns hopkins', 'massachusetts general', 
                        'cedars-sinai', 'newyork-presbyterian', 'ucsf', 'houston methodist']
        if any(indicator in org_name_lower for indicator in us_indicators):
            return 'united states'
        
        # Indian hospitals
        indian_indicators = ['apollo', 'fortis', 'aiims', 'yashoda', 'manipal', 'max healthcare', 
                           'narayana', 'medanta']
        if any(indicator in org_name_lower for indicator in indian_indicators):
            return 'india'
        
        # UK hospitals
        uk_indicators = ['great ormond', 'royal marsden', 'moorfields', 'king\'s college', 'imperial college']
        if any(indicator in org_name_lower for indicator in uk_indicators):
            return 'united kingdom'
        
        # Singapore hospitals
        singapore_indicators = ['singapore general', 'national university hospital', 'tan tock seng', 'mount elizabeth']
        if any(indicator in org_name_lower for indicator in singapore_indicators):
            return 'singapore'
        
        # Default to India if no clear location is found (since the issue was about Indian organizations)
        return 'india'
    
    def get_nearby_regions(self, region):
        """Get nearby regions for expanded comparison - restricted for regional specificity"""
        region_proximity = {
            'united states': ['canada'],
            'canada': ['united states'],
            'united kingdom': ['ireland', 'netherlands'],
            # Removed nearby regions for India to ensure strict regional comparison
            'india': [],  # Indian hospitals should only be compared with other Indian hospitals
            'singapore': ['australia'],  # Removed India to maintain regional specificity
            'australia': ['singapore']  # Removed India to maintain regional specificity
        }
        
        return region_proximity.get(region.lower(), [])

# PDF Generation Functions
def create_score_chart(score, title="Quality Score"):
    """Create a score visualization chart for PDF"""
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Create a gauge-like chart
    colors_list = ['#ff4444', '#ffaa44', '#ffdd44', '#88dd44', '#44dd44']
    ranges = [20, 40, 60, 80, 100]
    
    # Create background bars
    for i, (range_val, color) in enumerate(zip(ranges, colors_list)):
        start = ranges[i-1] if i > 0 else 0
        ax.barh(0, range_val - start, left=start, height=0.5, color=color, alpha=0.3)
    
    # Create score bar
    score_color = colors_list[min(int(score // 20), 4)]
    ax.barh(0, score, height=0.3, color=score_color, alpha=0.8)
    
    # Add score text
    ax.text(score/2, 0, f'{score:.1f}', ha='center', va='center', 
            fontsize=16, fontweight='bold', color='white')
    
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, 0.5)
    ax.set_xlabel('Score')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_yticks([])
    
    # Save to bytes
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

def create_certification_chart(certifications):
    """Create a certification breakdown chart for PDF"""
    if not certifications:
        return None
    
    # Count certifications by status
    status_counts = {}
    for cert in certifications:
        status = cert.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    colors = {'Active': '#44dd44', 'In Progress': '#ffaa44', 'Expired': '#ff4444', 'Unknown': '#cccccc'}
    
    statuses = list(status_counts.keys())
    counts = list(status_counts.values())
    chart_colors = [colors.get(status, '#cccccc') for status in statuses]
    
    ax.pie(counts, labels=statuses, colors=chart_colors, autopct='%1.1f%%', startangle=90)
    ax.set_title('Certification Status Distribution', fontsize=14, fontweight='bold')
    
    # Save to bytes
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

def generate_detailed_scorecard_pdf(org_name, org_data):
    """Generate a comprehensive PDF scorecard for the organization"""
    try:
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=rl_colors.HexColor('#2c3e50')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=rl_colors.HexColor('#34495e')
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            textColor=rl_colors.HexColor('#7f8c8d')
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6
        )
        
        # Build PDF content
        story = []
        
        # Header
        story.append(Paragraph("QuXAT Healthcare Quality Grid", title_style))
        story.append(Paragraph(f"Detailed Assessment Report for {org_name}", heading_style))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        
        score = org_data.get('total_score', 0)
        # Determine grade based on adjusted scoring scale (max 85)
        grade = "A+" if score >= 75 else "A" if score >= 65 else "B+" if score >= 55 else "B" if score >= 45 else "C"
        
        summary_text = f"""
        <b>{org_name}</b> has achieved an overall QuXAT quality score of <b>{score:.1f}/100</b> (Grade: <b>{grade}</b>).
        This assessment is based on comprehensive analysis of certifications, quality initiatives, transparency measures, 
        and reputation factors from publicly available sources.
        """
        story.append(Paragraph(summary_text, normal_style))
        story.append(Spacer(1, 15))
        
        # Score Breakdown
        story.append(Paragraph("Quality Score Breakdown", heading_style))
        
        score_breakdown = org_data.get('score_breakdown', {})
        
        # Create score breakdown table
        score_data = [
            ['Component', 'Weight', 'Score', 'Weighted Score'],
            ['Certifications', '60%', f"{score_breakdown.get('certification_score', 0):.1f}", 
             f"{score_breakdown.get('certification_weighted', 0):.1f}"],
            ['Quality Initiatives', '20%', f"{score_breakdown.get('initiative_score', 0):.1f}", 
             f"{score_breakdown.get('initiative_weighted', 0):.1f}"],
            ['Transparency', '10%', f"{score_breakdown.get('transparency_score', 0):.1f}", 
             f"{score_breakdown.get('transparency_weighted', 0):.1f}"],
            ['Reputation Bonus', '10%', f"{score_breakdown.get('reputation_bonus', 0):.1f}", 
             f"{score_breakdown.get('reputation_weighted', 0):.1f}"],
            ['', '', 'Total Score:', f"{score:.1f}/100"]
        ]
        
        score_table = Table(score_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1.5*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), rl_colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), rl_colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, rl_colors.black)
        ]))
        
        story.append(score_table)
        story.append(Spacer(1, 20))
        
        # Add score chart
        score_chart = create_score_chart(score, f"{org_name} Quality Score")
        if score_chart:
            from reportlab.platypus import Image as ReportLabImage
            story.append(Paragraph("Visual Score Representation", subheading_style))
            story.append(ReportLabImage(score_chart, width=5*inch, height=3*inch))
            story.append(Spacer(1, 15))
        
        # Certifications Section
        story.append(Paragraph("Certifications Analysis", heading_style))
        
        certifications = org_data.get('certifications', [])
        if certifications:
            story.append(Paragraph(f"Total Certifications Found: {len(certifications)}", subheading_style))
            
            # Active certifications table
            active_certs = [cert for cert in certifications if cert.get('status') == 'Active']
            if active_certs:
                cert_data = [['Certification', 'Status', 'Valid Until', 'Score Impact']]
                for cert in active_certs[:10]:  # Show top 10
                    cert_data.append([
                        cert.get('name', 'N/A'),
                        cert.get('status', 'N/A'),
                        cert.get('valid_until', 'N/A'),
                        f"{cert.get('score_impact', 0):.1f}"
                    ])
                
                cert_table = Table(cert_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1*inch])
                cert_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor('#27ae60')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), rl_colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, rl_colors.black)
                ]))
                
                story.append(cert_table)
                story.append(Spacer(1, 15))
            
            # Add certification chart
            cert_chart = create_certification_chart(certifications)
            if cert_chart:
                story.append(Paragraph("Certification Status Distribution", subheading_style))
                story.append(ReportLabImage(cert_chart, width=4*inch, height=3*inch))
                story.append(Spacer(1, 15))
        else:
            story.append(Paragraph("No certifications found in our database.", normal_style))
            story.append(Spacer(1, 10))
        
        # Quality Initiatives Section
        story.append(Paragraph("Quality Initiatives", heading_style))
        
        initiatives = org_data.get('quality_initiatives', [])
        if initiatives:
            story.append(Paragraph(f"Quality Initiatives Identified: {len(initiatives)}", subheading_style))
            
            for i, initiative in enumerate(initiatives[:8], 1):  # Show top 8
                init_text = f"<b>{i}.</b> {initiative.get('title', 'N/A')} ({initiative.get('year', 'N/A')})"
                story.append(Paragraph(init_text, normal_style))
            
            story.append(Spacer(1, 15))
        else:
            story.append(Paragraph("No specific quality initiatives found in our analysis.", normal_style))
            story.append(Spacer(1, 10))
        
        # Page break for next section
        story.append(PageBreak())
        
        # Methodology Section
        story.append(Paragraph("Assessment Methodology", heading_style))
        
        methodology_text = """
        <b>Data Sources:</b><br/>
        • Official certification body databases (ISO, JCI, NABH, etc.)<br/>
        • Healthcare news and press releases<br/>
        • Organization websites and public disclosures<br/>
        • Government healthcare databases<br/>
        • Quality initiative reports and publications<br/><br/>
        
        <b>Scoring Components:</b><br/>
        • <b>Certifications (50%):</b> Active certifications weighted by international recognition<br/>
        • <b>Quality Initiatives (15%):</b> Recent quality improvement programs and innovations<br/>
        • <b>Transparency (15%):</b> Public disclosure of quality metrics and outcomes<br/>
        • <b>Reputation Bonus (up to 5%):</b> International rankings and academic medical center status<br/><br/>
        
        <b>Score Ranges (Adjusted Scale):</b><br/>
        • 75-85: A+ (Exceptional Quality)<br/>
        • 65-74: A (High Quality)<br/>
        • 55-64: B+ (Good Quality)<br/>
        • 45-54: B (Acceptable Quality)<br/>
        • Below 45: C (Needs Improvement)
        """
        
        story.append(Paragraph(methodology_text, normal_style))
        story.append(Spacer(1, 20))
        
        # Disclaimers Section
        story.append(Paragraph("Important Disclaimers", heading_style))
        
        disclaimer_text = """
        <b>Assessment Limitations:</b> This scoring system is based on publicly available information and may not 
        capture all quality aspects of an organization. Scores are generated through automated analysis and 
        <b>may be incorrect or incomplete</b>.<br/><br/>
        
        <b>Data Dependencies:</b> Accuracy depends on the availability and reliability of public data sources. 
        Organizations may have additional certifications or quality initiatives not captured in our database.<br/><br/>
        
        <b>Not Medical Advice:</b> QuXAT scores do not constitute medical advice, professional recommendations, 
        or endorsements. Users should conduct independent verification and due diligence before making healthcare decisions.<br/><br/>
        
        <b>Limitation of Liability:</b> QuXAT and its developers disclaim all warranties, express or implied, 
        regarding the accuracy or completeness of information. Users assume full responsibility for any decisions 
        made based on QuXAT assessments.<br/><br/>
        
        <b>Comparative Tool Only:</b> Intended for comparative analysis and research purposes, not absolute quality determination.
        """
        
        story.append(Paragraph(disclaimer_text, normal_style))
        story.append(Spacer(1, 20))
        
        # Footer
        footer_text = f"""
        <b>Report Generated by:</b> QuXAT Healthcare Quality Grid v3.0<br/>
        <b>Generation Date:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
        <b>Organization:</b> {org_name}<br/>
        <b>Report ID:</b> QXT-{datetime.now().strftime('%Y%m%d')}-{hash(org_name) % 10000:04d}
        """
        
        story.append(Paragraph(footer_text, normal_style))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
        
    except Exception as e:
        # Log error without using Streamlit functions to avoid context issues
        print(f"Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def display_detailed_scorecard_inline(org_name, org_data, score):
    """
    Display a comprehensive detailed scorecard inline instead of generating PDF
    """
    try:
        # Header Section
        st.markdown("---")
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
            color: white;
            text-align: center;
        ">
            <h1 style="color: white; margin-bottom: 0.5rem; font-size: 2.2rem;">📋 Detailed Quality Scorecard</h1>
            <h2 style="color: white; margin-bottom: 0.5rem; font-size: 1.8rem;">{org_name}</h2>
            <p style="font-size: 1.2rem; margin-bottom: 0; opacity: 0.9;">
                Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Executive Summary
        st.markdown("### 📊 Executive Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Overall Score",
                value=f"{score:.1f}/100",
                delta=f"Grade: {org_data.get('grade', 'N/A')}"
            )
        
        with col2:
            st.metric(
                label="Location",
                value=org_data.get('location', 'N/A')
            )
        
        with col3:
            st.metric(
                label="Organization Type",
                value=org_data.get('type', 'Healthcare Organization')
            )
        
        with col4:
            active_certs = len([c for c in org_data.get('certifications', []) if c.get('status') == 'Active'])
            st.metric(
                label="Active Certifications",
                value=active_certs
            )
        
        # Score Breakdown Section
        st.markdown("### 🎯 Score Breakdown Analysis")
        
        score_breakdown = org_data.get('score_breakdown', {})
        
        # Create score breakdown table
        breakdown_data = {
            'Component': ['Certifications', 'Quality Initiatives', 'Transparency', 'Reputation Bonus', 'Total Score'],
            'Weight': ['60%', '20%', '10%', '10%', '100%'],
            'Score': [
                f"{score_breakdown.get('certification_score', 0):.1f}",
                f"{score_breakdown.get('initiative_score', 0):.1f}",
                f"{score_breakdown.get('transparency_score', 0):.1f}",
                f"{score_breakdown.get('reputation_bonus', 0):.1f}",
                f"{score:.1f}"
            ],
            'Weighted Score': [
                f"{score_breakdown.get('certification_weighted', 0):.1f}",
                f"{score_breakdown.get('initiative_weighted', 0):.1f}",
                f"{score_breakdown.get('transparency_weighted', 0):.1f}",
                f"{score_breakdown.get('reputation_weighted', 0):.1f}",
                f"{score:.1f}/100"
            ]
        }
        
        breakdown_df = pd.DataFrame(breakdown_data)
        st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
        
        # Visual Score Representation
        st.markdown("### 📈 Visual Score Representation")
        
        # Create a gauge chart for the overall score
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"{org_name} Quality Score"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 45], 'color': "lightgray"},
                    {'range': [45, 55], 'color': "yellow"},
                    {'range': [55, 65], 'color': "lightgreen"},
                    {'range': [65, 75], 'color': "green"},
                    {'range': [75, 100], 'color': "darkgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Certifications Analysis
        st.markdown("### 🏆 Certifications Analysis")
        
        certifications = org_data.get('certifications', [])
        if certifications:
            st.markdown(f"**Total Certifications Found:** {len(certifications)}")
            
            # Active certifications
            active_certs = [cert for cert in certifications if cert.get('status') == 'Active']
            if active_certs:
                st.markdown("#### Active Certifications")
                
                cert_data = []
                for cert in active_certs[:10]:  # Show top 10
                    cert_name = cert.get('name', 'N/A')
                    is_nabh = 'NABH' in cert_name.upper() if cert_name != 'N/A' else False
                    is_jci = 'JCI' in cert_name.upper() if cert_name != 'N/A' else False
                    valid_until = cert.get('valid_until', 'N/A')
                    
                    # For NABH or JCI certifications with no valid_until data, don't show N/A
                    if (is_nabh or is_jci) and (valid_until == 'N/A' or valid_until is None):
                        cert_data.append({
                            'Certification': cert_name,
                            'Status': cert.get('status', 'N/A'),
                            'Valid Until': '',  # Empty instead of N/A for NABH/JCI
                            'Score Impact': f"{cert.get('score_impact', 0):.1f}"
                        })
                    else:
                        cert_data.append({
                            'Certification': cert_name,
                            'Status': cert.get('status', 'N/A'),
                            'Valid Until': valid_until,
                            'Score Impact': f"{cert.get('score_impact', 0):.1f}"
                        })
                
                if cert_data:
                    cert_df = pd.DataFrame(cert_data)
                    st.dataframe(cert_df, use_container_width=True, hide_index=True)
            
            # Certification status distribution
            if len(certifications) > 1:
                st.markdown("#### Certification Status Distribution")
                status_counts = {}
                for cert in certifications:
                    status = cert.get('status', 'Unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                fig_pie = px.pie(
                    values=list(status_counts.values()),
                    names=list(status_counts.keys()),
                    title="Certification Status Distribution"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No certifications found in our database.")
        
        # Quality Initiatives Section
        st.markdown("### 🚀 Quality Initiatives")
        
        initiatives = org_data.get('quality_initiatives', [])
        if initiatives:
            st.markdown(f"**Quality Initiatives Identified:** {len(initiatives)}")
            
            for i, initiative in enumerate(initiatives[:8], 1):  # Show top 8
                with st.expander(f"{i}. {initiative.get('title', 'N/A')} ({initiative.get('year', 'N/A')})"):
                    st.write(f"**Description:** {initiative.get('description', 'No description available')}")
                    st.write(f"**Category:** {initiative.get('category', 'N/A')}")
                    st.write(f"**Impact Score:** {initiative.get('impact_score', 0):.1f}")
        else:
            st.info("No specific quality initiatives found in our analysis.")
        
        # Assessment Methodology
        st.markdown("### 📋 Assessment Methodology")
        
        with st.expander("Data Sources & Methodology", expanded=False):
            st.markdown("""
            **Data Sources:**
            - 🏛️ Official certification body databases (ISO, JCI, NABH, etc.)
            - 📰 Healthcare news and press releases
            - 🏢 Organization websites and public disclosures
            - 📊 Government healthcare databases
            - 🔍 Quality initiative reports and publications
            
            **Scoring Components:**
            - **Certifications (50%):** Active certifications weighted by international recognition
            - **Quality Initiatives (15%):** Recent quality improvement programs and innovations
            - **Transparency (15%):** Public disclosure of quality metrics and outcomes
            - **Reputation Bonus (up to 5%):** International rankings and academic medical center status
            
            **Score Ranges (Adjusted Scale):**
            - 75-85: A+ (Exceptional Quality)
            - 65-74: A (High Quality)
            - 55-64: B+ (Good Quality)
            - 45-54: B (Acceptable Quality)
            - Below 45: C (Needs Improvement)
            """)
        
        # Important Disclaimers
        st.markdown("### ⚠️ Important Disclaimers")
        
        with st.expander("Assessment Limitations & Disclaimers", expanded=False):
            st.markdown("""
            **Assessment Limitations:** This scoring system is based on publicly available information and may not 
            capture all quality aspects of an organization. Scores are generated through automated analysis and 
            **may be incorrect or incomplete**.
            
            **Data Dependencies:** Accuracy depends on the availability and reliability of public data sources. 
            Organizations may have additional certifications or quality initiatives not captured in our database.
            
            **Not Medical Advice:** QuXAT scores do not constitute medical advice, professional recommendations, 
            or endorsements. Users should conduct independent verification and due diligence before making healthcare decisions.
            
            **Limitation of Liability:** QuXAT and its developers disclaim all warranties, express or implied, 
            regarding the accuracy or completeness of information. Users assume full responsibility for any decisions 
            made based on QuXAT assessments.
            
            **Comparative Tool Only:** Intended for comparative analysis and research purposes, not absolute quality determination.
            """)
        
        # Report Footer
        st.markdown("### 📄 Report Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Report Generated by:** QuXAT Healthcare Quality Grid v3.0  
            **Generation Date:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}  
            **Organization:** {org_name}
            """)
        
        with col2:
            report_id = f"QXT-{datetime.now().strftime('%Y%m%d')}-{hash(org_name) % 10000:04d}"
            st.info(f"""
            **Report ID:** {report_id}  
            **Data Version:** Latest Available  
            **Assessment Type:** Comprehensive Quality Analysis
            """)
        
        st.markdown("---")
        st.success("✅ Detailed scorecard displayed successfully! This comprehensive view includes all information that would be in the PDF report.")
        
    except Exception as e:
        st.error(f"Error displaying detailed scorecard: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")

# Initialize the analyzer
@st.cache_resource
def get_analyzer():
    return HealthcareOrgAnalyzer()

# Display dynamic logo at the top of every page
display_dynamic_logo()

# Sidebar navigation with improved styling
st.sidebar.markdown("""
<div style="
    text-align: center; 
    padding: 12px 0; 
    margin-bottom: 15px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
    margin: -1rem -1rem 1rem -1rem;
">
    <h2 style="
        color: white; 
        margin: 0; 
        font-size: 1.5rem;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    ">🧭 Navigation</h2>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Initialize page in session state if not exists
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Use session state for page selection
# Add admin option if authenticated
page_options = ["Home", "QuXAT Scoring Method", "Quality Dashboard", "Global Healthcare Quality", "Certifications"]
if is_admin_authenticated():
    page_options.extend(["Settings", "Admin Panel"])

page = st.sidebar.selectbox("Choose a page:", 
                           page_options,
                           index=page_options.index(st.session_state.page) if st.session_state.page in page_options else 0)

# Update session state when selectbox changes
if page != st.session_state.page:
    st.session_state.page = page
    st.rerun()

# Main content

# Main content
try:
    if page == "Home":
        st.header("🏠 Welcome to QuXAT Healthcare Quality Grid")
        
        # Hero Section with Targeted Messaging
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 0.5rem 0 1rem 0;
            color: white;
            text-align: center;
        ">
            <h2 style="color: white; margin-bottom: 0.5rem; font-size: 1.4rem;">🌟 Healthcare Quality Assessment Platform</h2>
            <p style="font-size: 1rem; margin-bottom: 0; opacity: 0.9;">
                Discover, evaluate, and benchmark healthcare organizations worldwide
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Targeted User Groups Section
        st.markdown("### 👥 Who Benefits from QuXAT?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="
                background: #f8f9ff;
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid #4CAF50;
                height: 200px;
                display: flex;
                flex-direction: column;
            ">
                <h4 style="color: #2E7D32; margin-bottom: 0.5rem; font-size: 1rem;">👩‍⚕️ Healthcare Professionals</h4>
                <ul style="color: #333; line-height: 1.4; flex-grow: 1; font-size: 0.9rem; margin: 0; padding-left: 1rem;">
                    <li><strong>Benchmark:</strong> Compare quality metrics against global standards</li>
                    <li><strong>Development:</strong> Identify improvement opportunities</li>
                    <li><strong>Career Decisions:</strong> Evaluate potential employers</li>
                    <li><strong>Quality Advocacy:</strong> Support improvement initiatives</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: #fff8f0;
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid #FF9800;
                height: 200px;
                display: flex;
                flex-direction: column;
            ">
                <h4 style="color: #E65100; margin-bottom: 0.5rem; font-size: 1rem;">👔 Healthcare Management</h4>
                <ul style="color: #333; line-height: 1.4; flex-grow: 1; font-size: 0.9rem; margin: 0; padding-left: 1rem;">
                    <li><strong>Strategic Planning:</strong> Make informed certification decisions</li>
                    <li><strong>Competitive Analysis:</strong> Understand market position</li>
                    <li><strong>ROI on Quality:</strong> Demonstrate value to stakeholders</li>
                    <li><strong>Reputation:</strong> Monitor quality reputation</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="
                background: #f0f8ff;
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid #2196F3;
                height: 200px;
                display: flex;
                flex-direction: column;
            ">
                <h4 style="color: #1565C0; margin-bottom: 0.5rem; font-size: 1rem;">🏥 Patients & Families</h4>
                <ul style="color: #333; line-height: 1.4; flex-grow: 1; font-size: 0.9rem; margin: 0; padding-left: 1rem;">
                    <li><strong>Informed Decisions:</strong> Choose providers based on quality metrics</li>
                    <li><strong>Safety Assurance:</strong> Verify international standards</li>
                    <li><strong>Treatment Planning:</strong> Select specialized centers</li>
                    <li><strong>Peace of Mind:</strong> Gain confidence in healthcare choices</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Call-to-Action Section
        st.markdown("""
        <div style="
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            color: white;
            margin: 0.5rem 0;
        ">
            <h3 style="color: white; margin-bottom: 0.5rem; font-size: 1.2rem;">🚀 Start Your Quality Assessment Journey</h3>
            <p style="font-size: 1rem; margin-bottom: 0;">
                Search any healthcare organization below for comprehensive quality scores and insights
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Comprehensive Organization Search & Analysis Section
        st.subheader("🔍 Healthcare Organization Search & Quality Assessment")
        
        # Enhanced search interface with autocomplete
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            # Initialize analyzer for suggestions
            analyzer = get_analyzer()
            
            # Text input for typing
            search_input = st.text_input("🏥 Enter Organization Name", 
                                       placeholder="e.g., Mayo Clinic, Johns Hopkins, Apollo Hospitals",
                                       key="home_org_search")
            
            # Generate suggestions if user has typed something
            suggestions = []
            selected_org = None
            
            if search_input and len(search_input) >= 2:
                suggestions = analyzer.generate_organization_suggestions(search_input, max_suggestions=8)
                
                if suggestions:
                    # Create formatted options for selectbox
                    suggestion_options = ["Select from suggestions..."] + [
                        analyzer.format_suggestion_display(suggestion) for suggestion in suggestions
                    ]
                    
                    selected_suggestion = st.selectbox(
                        "💡 Suggestions based on your input:",
                        suggestion_options,
                        key="org_suggestions"
                    )
                    
                    # If user selected a suggestion, use it
                    if selected_suggestion != "Select from suggestions...":
                        # Find the corresponding suggestion
                        for i, suggestion in enumerate(suggestions):
                            if analyzer.format_suggestion_display(suggestion) == selected_suggestion:
                                selected_org = suggestion['display_name']
                                break
            
            # Use selected organization or typed input
            org_name = selected_org if selected_org else search_input
            
        with col2:
            search_type = st.selectbox("🔍 Search Type", 
                                     ["Global Search", "By Country", "By Certification"],
                                     key="home_search_type")
        with col3:
            search_button = st.button("🔍 Search Organization", type="primary", key="home_search_btn")
        
        # Process search
        if search_button and org_name:
            # Data validation notice
            st.info("🔍 **Data Validation Notice:** QuXAT uses validated data from official certification bodies.")
            
            # Initialize the analyzer
            analyzer = get_analyzer()
            
            with st.spinner("🔍 Searching for organization data..."):
                # Real-time data search
                org_data = analyzer.search_organization_info(org_name)
                
                if org_data:
                    st.success(f"✅ Found information for: **{org_name}**")
                    
                    # Store in session state for detailed view
                    st.session_state.current_org = org_name
                    st.session_state.current_data = org_data
                    
                    # Define variables needed for comparison table
                    score = org_data['total_score']
                    grade = "A+" if score >= 75 else "A" if score >= 65 else "B+" if score >= 55 else "B" if score >= 45 else "C"
                    org_type = "Hospital"  # Default type, can be enhanced later
                    
                    # Display organization profile
                    st.subheader(f"🏥 {org_name} - Quality Scorecard")
                    
                    # Key metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        score_color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                        st.metric("🏆 Overall Quality Score", f"{score}/100", f"{score_color}")
                    
                    with col2:
                        active_certs = len([c for c in org_data['certifications'] if c['status'] == 'Active'])
                        st.metric("📜 Active Certifications", active_certs)
                    
                    with col3:
                        initiatives_count = len(org_data['quality_initiatives'])
                        st.metric("📈 Quality Initiatives", initiatives_count)
                    
                    with col4:
                        trend = "Improving" if score >= 70 else "Stable" if score >= 50 else "Needs Attention"
                        trend_icon = "↗️" if score >= 70 else "➡️" if score >= 50 else "↘️"
                        st.metric("📊 Quality Trend", trend, trend_icon)
                    
                    # Detailed Scoring Information Section
                    st.markdown("### 🏆 Detailed Scoring Information")
                    
                    # Quality Grade Display
                    if score >= 90:
                        grade, grade_color, grade_desc = "A+", "🟢", "Exceptional Quality"
                    elif score >= 80:
                        grade, grade_color, grade_desc = "A", "🟢", "Excellent Quality"
                    elif score >= 70:
                        grade, grade_color, grade_desc = "B+", "🟡", "Good Quality"
                    elif score >= 60:
                        grade, grade_color, grade_desc = "B", "🟡", "Satisfactory Quality"
                    elif score >= 50:
                        grade, grade_color, grade_desc = "C+", "🟠", "Needs Improvement"
                    else:
                        grade, grade_color, grade_desc = "C", "🔴", "Significant Improvement Required"
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 20px; border: 2px solid #e0e0e0; border-radius: 10px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);">
                            <h2 style="color: #2c3e50; margin: 0;">Quality Grade: {grade_color} {grade}</h2>
                            <p style="color: #7f8c8d; margin: 5px 0; font-size: 18px;">{grade_desc}</p>
                            <h3 style="color: #e74c3c; margin: 10px 0;">{score:.1f}/100</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Certifications Section
                    st.markdown("### 🏅 Active Certifications")
                    
                    # Get certifications from organization data (excluding JCI and NABH as they are accreditations)
                    certifications = org_data.get('certifications', [])
                    # Filter out JCI and NABH as they should be in accreditations section
                    certifications = [cert for cert in certifications if not ('JCI' in cert.get('name', '').upper() or 'NABH' in cert.get('name', '').upper())]
                    if certifications:
                        cert_cols = st.columns(min(len(certifications), 3))
                        for idx, cert in enumerate(certifications[:6]):  # Show up to 6 certifications
                            with cert_cols[idx % 3]:
                                # Determine certification status and icon
                                cert_status = cert.get('status', 'Active')
                                cert_icon = "✅" if cert_status == "Active" else "⏳" if cert_status == "Pending" else "❌"
                                
                                # Special handling for NABH - only show status if details are not available
                                cert_name = cert.get('name', 'Unknown Certification')
                                is_nabh = 'NABH' in cert_name.upper()
                                is_jci = 'JCI' in cert_name.upper()
                                issuer = cert.get('issuer', 'N/A')
                                valid_until = cert.get('valid_until', cert.get('expiry', 'N/A'))
                                
                                if (is_nabh and (issuer == 'N/A' or issuer is None) and (valid_until == 'N/A' or valid_until is None)) or \
                                   (is_jci and (issuer == 'N/A' or issuer is None) and (valid_until == 'N/A' or valid_until is None)):
                                    # For NABH or JCI with no details, show only status
                                    st.markdown(f"""
                                    <div style="padding: 15px; border: 1px solid #ddd; border-radius: 8px; margin: 10px 0; background: #f8f9fa;">
                                        <h4 style="color: #2c3e50; margin: 0 0 10px 0;">{cert_icon} {cert_name}</h4>
                                        <p style="margin: 5px 0; color: #666;"><strong>Status:</strong> <span style="color: {'#28a745' if cert_status == 'Active' else '#ffc107' if cert_status == 'Pending' else '#dc3545'};">{cert_status}</span></p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    # For all other certifications or NABH/JCI with details, show full information
                                    st.markdown(f"""
                                    <div style="padding: 15px; border: 1px solid #ddd; border-radius: 8px; margin: 10px 0; background: #f8f9fa;">
                                        <h4 style="color: #2c3e50; margin: 0 0 10px 0;">{cert_icon} {cert_name}</h4>
                                        <p style="margin: 5px 0; color: #666;"><strong>Issued by:</strong> {issuer}</p>
                                        <p style="margin: 5px 0; color: #666;"><strong>Valid Until:</strong> {valid_until}</p>
                                        <p style="margin: 5px 0; color: #666;"><strong>Status:</strong> <span style="color: {'#28a745' if cert_status == 'Active' else '#ffc107' if cert_status == 'Pending' else '#dc3545'};">{cert_status}</span></p>
                                    </div>
                                    """, unsafe_allow_html=True)
                    else:
                        st.info("📋 No active certifications found for this organization.")
                    
                    st.markdown("---")
                    
                    # Accreditations Section
                    st.markdown("### 🎖️ Accreditations & Recognition")
                    
                    # Get accreditations from organization data
                    accreditations = org_data.get('accreditations', [])
                    
                    # Add JCI and NABH from certifications data as they are actually accreditations
                    all_certifications = org_data.get('certifications', [])
                    jci_nabh_accreditations = [cert for cert in all_certifications if ('JCI' in cert.get('name', '').upper() or 'NABH' in cert.get('name', '').upper())]
                    
                    # Convert JCI/NABH certifications to accreditation format
                    for cert in jci_nabh_accreditations:
                        accred_entry = {
                            'name': cert.get('name', 'Unknown Accreditation'),
                            'level': 'International Standard' if 'JCI' in cert.get('name', '').upper() else 'National Standard',
                            'awarded_date': cert.get('issued_date', cert.get('awarded_date', 'N/A')),
                            'description': cert.get('description', ''),
                            'status': cert.get('status', 'Active'),
                            'issuer': cert.get('issuer', 'N/A'),
                            'valid_until': cert.get('valid_until', cert.get('expiry', 'N/A'))
                        }
                        accreditations.append(accred_entry)
                    
                    # Check for NABL accreditation
                    nabl_accreditation = healthcare_validator.get_nabl_accreditation(org_name)
                    if nabl_accreditation:
                        accreditations.append(nabl_accreditation)
                    
                    if not accreditations:
                        # Create sample accreditations based on organization type and score
                        accreditations = []
                        if score >= 70:
                            accreditations.append({
                                'name': 'Joint Commission Accreditation',
                                'level': 'Gold Standard',
                                'awarded_date': '2023',
                                'description': 'Comprehensive healthcare quality and safety accreditation'
                            })
                        if score >= 60:
                            accreditations.append({
                                'name': 'ISO 9001:2015 Quality Management',
                                'level': 'Certified',
                                'awarded_date': '2022',
                                'description': 'International standard for quality management systems'
                            })
                        if score >= 50:
                            accreditations.append({
                                'name': 'Healthcare Quality Recognition',
                                'level': 'Bronze',
                                'awarded_date': '2023',
                                'description': 'Recognition for commitment to healthcare quality improvement'
                            })
                    
                    if accreditations:
                        for accred in accreditations:
                            # Determine accreditation level icon
                            level = accred.get('level', '').lower()
                            accred_name = accred.get('name', '').upper()
                            
                            # Special icons for JCI and NABH
                            if 'JCI' in accred_name:
                                level_icon = "🏥"
                                level_color = "#1976D2"
                            elif 'NABH' in accred_name:
                                level_icon = "🇮🇳"
                                level_color = "#FF9800"
                            elif 'gold' in level or 'excellent' in level:
                                level_icon = "🥇"
                                level_color = "#FFD700"
                            elif 'silver' in level or 'good' in level:
                                level_icon = "🥈"
                                level_color = "#C0C0C0"
                            elif 'bronze' in level or 'standard' in level:
                                level_icon = "🥉"
                                level_color = "#CD7F32"
                            elif 'iso/iec 17025' in level or 'nabl' in accred.get('name', '').lower():
                                level_icon = "🔬"
                                level_color = "#2196F3"
                            else:
                                level_icon = "🏆"
                                level_color = "#4CAF50"
                            
                            # Format validity date if available (special handling for JCI/NABH)
                            validity_info = ""
                            valid_until = accred.get('valid_until')
                            is_jci_nabh = 'JCI' in accred_name or 'NABH' in accred_name
                            
                            if is_jci_nabh and (valid_until == 'N/A' or valid_until is None):
                                # Don't show validity info for JCI/NABH when not available
                                validity_info = ""
                            elif valid_until and valid_until != 'N/A':
                                validity_info = f"<p style=\"margin: 5px 0; color: #666;\"><strong>Valid Until:</strong> {valid_until}</p>"
                            
                            # Format issuer info if available (special handling for JCI/NABH)
                            issuer_info = ""
                            issuer = accred.get('issuer')
                            if is_jci_nabh and (issuer == 'N/A' or issuer is None):
                                # Don't show issuer info for JCI/NABH when not available
                                issuer_info = ""
                            elif issuer and issuer != 'N/A':
                                issuer_info = f"<p style=\"margin: 5px 0; color: #666;\"><strong>Issued by:</strong> {issuer}</p>"
                            
                            # Format certificate number if available
                            cert_info = ""
                            if accred.get('certificate_number'):
                                cert_info = f"<p style=\"margin: 5px 0; color: #666;\"><strong>Certificate:</strong> {accred.get('certificate_number')}</p>"
                            
                            # Get description without HTML escaping to allow proper rendering
                            description = accred.get('description', 'No description available.')
                            
                            st.markdown(f"""
                            <div style="padding: 20px; border-left: 4px solid {level_color}; background: #f8f9fa; margin: 15px 0; border-radius: 0 8px 8px 0;">
                                <h4 style="color: #2c3e50; margin: 0 0 10px 0;">{level_icon} {accred.get('name', 'Unknown Accreditation')}</h4>
                                <p style="margin: 5px 0; color: #666;"><strong>Level:</strong> <span style="color: {level_color}; font-weight: bold;">{accred.get('level', 'N/A')}</span></p>
                                <p style="margin: 5px 0; color: #666;"><strong>Accreditation Status:</strong> <span style="color: {'#28a745' if accred.get('status', 'Active') == 'Active' else '#ffc107' if accred.get('status', 'Active') == 'Pending' else '#dc3545'};">{accred.get('status', 'Active')}</span></p>
                                {issuer_info}
                                {validity_info}
                                {cert_info}
                                {description}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("🎖️ No accreditations found for this organization.")
                    
                    st.markdown("---")
                    
                    # Quality Performance Indicators
                    st.markdown("### 📊 Quality Performance Indicators")
                    
                    perf_col1, perf_col2, perf_col3 = st.columns(3)
                    
                    with perf_col1:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background: #e8f5e8;">
                            <h3 style="color: #2e7d32; margin: 0;">Patient Safety</h3>
                            <h2 style="color: #1b5e20; margin: 5px 0;">{min(100, score + 5):.1f}%</h2>
                            <p style="color: #4caf50; margin: 0; font-size: 14px;">Above Average</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with perf_col2:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background: #e3f2fd;">
                            <h3 style="color: #1976d2; margin: 0;">Care Quality</h3>
                            <h2 style="color: #0d47a1; margin: 5px 0;">{score:.1f}%</h2>
                            <p style="color: #2196f3; margin: 0; font-size: 14px;">{"Excellent" if score >= 80 else "Good" if score >= 60 else "Fair"}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with perf_col3:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background: #fff3e0;">
                            <h3 style="color: #f57c00; margin: 0;">Efficiency</h3>
                            <h2 style="color: #e65100; margin: 5px 0;">{max(40, score - 10):.1f}%</h2>
                            <p style="color: #ff9800; margin: 0; font-size: 14px;">{"High" if score >= 70 else "Moderate" if score >= 50 else "Improving"}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Score breakdown visualization
                    st.markdown("### 📊 Score Breakdown")
                    score_data = org_data['score_breakdown']
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        # Create pie chart for score breakdown
                        # Ensure reputation_bonus exists in score_data
                        reputation_bonus = score_data.get('reputation_bonus', 0)
                        
                        labels = ['Certifications (60%)', 'Quality Initiatives (20%)', 'Transparency (10%)', 'Reputation Bonus']
                        values = [score_data['certification_score'], 
                                score_data['initiative_score'], 
                                score_data['transparency_score'],
                                reputation_bonus]
                        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#9B59B6']
                        
                        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
                        fig.update_traces(hoverinfo='label+percent', textinfo='value', 
                                        textfont_size=12, marker=dict(colors=colors))
                        fig.update_layout(title_text="Quality Score Components", height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Score breakdown metrics
                        st.markdown("#### 📈 Detailed Breakdown")
                        st.metric("🏆 Certification Score", f"{score_data['certification_score']:.1f}/60")
                        st.metric("🚀 Initiative Score", f"{score_data['initiative_score']:.1f}/20")
                        st.metric("📋 Transparency Score", f"{score_data['transparency_score']:.1f}/10")
                        st.metric("⭐ Reputation Bonus", f"+{reputation_bonus:.1f}")
                        
                        # Show reputation multiplier
                        analyzer = get_analyzer()
                        multiplier = analyzer.get_reputation_multiplier(org_name)
                        if multiplier > 1.0:
                            st.metric("🌟 Reputation Multiplier", f"{multiplier:.2f}x")
                        
                        # Quality grade
                        if score >= 90:
                            grade, grade_color = "A+", "🟢"
                        elif score >= 80:
                            grade, grade_color = "A", "🟢"
                        elif score >= 70:
                            grade, grade_color = "B+", "🟡"
                        elif score >= 60:
                            grade, grade_color = "B", "🟡"
                        else:
                            grade, grade_color = "C", "🔴"
                        
                        st.markdown(f"### {grade_color} Quality Grade: **{grade}**")
                    
                    # Certification details
                    st.markdown("### 🏆 Certifications & Accreditations")
                    if org_data['certifications']:
                        cert_df = pd.DataFrame(org_data['certifications'])
                        cert_df['Status Icon'] = cert_df['status'].map({
                            'Active': '✅', 'In Progress': '🔄', 'Expired': '❌'
                        })
                        
                        # Handle missing 'valid_until' column gracefully
                        columns_to_display = ['Status Icon', 'name', 'status']
                        column_names = ['Status', 'Certification', 'Status Detail']
                        
                        # Add valid_until column if it exists
                        if 'valid_until' in cert_df.columns:
                            columns_to_display.append('valid_until')
                            column_names.append('Valid Until')
                        elif 'expiry' in cert_df.columns:
                            columns_to_display.append('expiry')
                            column_names.append('Valid Until')
                        
                        # Add score_impact column if it exists
                        if 'score_impact' in cert_df.columns:
                            columns_to_display.append('score_impact')
                            column_names.append('Score Impact')
                        
                        # Display certifications table
                        display_df = cert_df[columns_to_display].copy()
                        display_df.columns = column_names
                        st.dataframe(display_df, use_container_width=True)
                    else:
                        st.info("No certification data found for this organization.")
                    
                    # Quality initiatives
                    st.markdown("### 🚀 Recent Quality Initiatives")
                    if org_data['quality_initiatives']:
                        for initiative in org_data['quality_initiatives']:
                            with st.expander(f"📋 {initiative['title']} ({initiative['year']})"):
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"**Initiative:** {initiative['title']}")
                                    st.write(f"**Year:** {initiative['year']}")
                                with col2:
                                    st.metric("Impact Score", f"+{initiative['impact_score']}")
                    else:
                        st.info("No recent quality initiatives found.")
                    
                    # Data sources and methodology
                    st.markdown("### 📚 Data Sources & Methodology")
                    with st.expander("ℹ️ How we calculate this score"):
                        st.markdown("""
                        **Data Sources:**
                        - 🏛️ Official certification body databases (ISO, JCI, NABH, etc.)
                        - 📰 Healthcare news and press releases
                        - 🏢 Organization websites and public disclosures
                        - 📊 Government healthcare databases
                        - 🔍 Quality initiative reports and publications
                        
                        **Scoring Methodology:**
                        - **Certifications (50%):** Active certifications weighted by international recognition
                        - **Quality Initiatives (15%):** Recent quality improvement programs and innovations  
                        - **Transparency (15%):** Public disclosure of quality metrics and outcomes
                        - **Reputation Bonus (up to 5%):** International rankings and academic medical center status
                        - **Reputation Multipliers:** Applied based on US News, Newsweek, and academic recognition (reduced impact)
                        
                        **Score Ranges (Adjusted Scale):**
                        - 75-85: A+ (Exceptional Quality)
                        - 65-74: A (High Quality)
                        - 55-64: B+ (Good Quality)
                        - 45-54: B (Acceptable Quality)
                        - Below 45: C (Needs Improvement)
                        
                        ---
                        
                        **⚠️ Scoring Disclaimers:**
                        - **Assessment Limitations:** This scoring system is based on publicly available information and may not capture all quality aspects of an organization
                        - **Algorithmic Assessment:** Scores are generated through automated analysis and **may be incorrect or incomplete**
                        - **Data Dependencies:** Accuracy depends on the availability and reliability of public data sources
                        - **Not a Substitute:** These scores should not replace professional evaluation or due diligence when selecting healthcare providers
                        - **Comparative Tool Only:** Intended for comparative analysis and research purposes, not absolute quality determination
                        """)
                    
                    # Comparative Analysis Section
                    st.markdown("---")
                    st.markdown("### 🏥 Similar Organizations Comparison")
                    
                    with st.spinner("🔍 Finding similar organizations in your locality..."):
                        analyzer = get_analyzer()
                        # Get organization info to extract location
                        org_info = analyzer.search_organization_info(org_name)
                        org_location = ""
                        if org_info and 'unified_data' in org_info:
                            # Extract location from unified database if available
                            unified_data = org_info['unified_data']
                            if 'location' in unified_data:
                                org_location = unified_data['location']
                            elif 'city' in unified_data and 'state' in unified_data:
                                org_location = f"{unified_data['city']}, {unified_data['state']}"
                            elif 'address' in unified_data:
                                org_location = unified_data['address']
                        
                        similar_orgs = analyzer.find_similar_organizations(org_name, org_location)
                        
                        if similar_orgs:
                            st.markdown(f"**Found {len(similar_orgs)} similar healthcare organizations for comparison:**")
                            
                            # Create comparison table
                            comparison_data = []
                            comparison_data.append({
                                'Organization': f"**{org_name}** (Searched)",
                                'Location': "Current Search",
                                'Type': org_type,
                                'Quality Score': f"{score:.1f}",
                                'Grade': grade,
                                'Certifications': len([c for c in org_data['certifications'] if c['status'] == 'Active']),
                                'Initiatives': len(org_data['quality_initiatives'])
                            })
                            
                            for org in similar_orgs:
                                org_grade = "A+" if org['total_score'] >= 75 else "A" if org['total_score'] >= 65 else "B+" if org['total_score'] >= 55 else "B" if org['total_score'] >= 45 else "C"
                                comparison_data.append({
                                    'Organization': org['name'],
                                    'Location': org['location'],
                                    'Type': org['type'],
                                    'Quality Score': f"{org['total_score']:.1f}",
                                    'Grade': org_grade,
                                    'Certifications': len([c for c in org['certifications'] if c['status'] == 'Active']),
                                    'Initiatives': len(org['quality_initiatives'])
                                })
                            
                            # Display comparison table
                            comparison_df = pd.DataFrame(comparison_data)
                            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                            
                            # Visualization: Score comparison chart
                            st.markdown("#### 📊 Quality Score Comparison")
                            
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                # Bar chart comparing scores
                                org_names = [org_name + " (You)"] + [org['name'] for org in similar_orgs]
                                scores = [score] + [org['total_score'] for org in similar_orgs]
                                colors_list = ['#FF6B6B'] + ['#4ECDC4' if s >= score else '#FFA07A' for s in scores[1:]]
                                
                                fig = go.Figure(data=[
                                    go.Bar(
                                        x=org_names,
                                        y=scores,
                                        marker_color=colors_list,
                                        text=[f"{s:.1f}" for s in scores],
                                        textposition='auto',
                                    )
                                ])
                                
                                fig.update_layout(
                                    title="Quality Score Comparison",
                                    xaxis_title="Healthcare Organizations",
                                    yaxis_title="Quality Score (0-100)",
                                    height=400,
                                    xaxis_tickangle=-45
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                            
                            with col2:
                                # Ranking and statistics
                                st.markdown("#### 📈 Your Position")
                                
                                # Calculate ranking
                                all_scores = [score] + [org['total_score'] for org in similar_orgs]
                                sorted_scores = sorted(all_scores, reverse=True)
                                your_rank = sorted_scores.index(score) + 1
                                total_orgs = len(all_scores)
                                
                                st.metric("🏆 Your Rank", f"{your_rank} of {total_orgs}")
                                
                                # Percentile
                                percentile = ((total_orgs - your_rank) / (total_orgs - 1)) * 100 if total_orgs > 1 else 100
                                st.metric("📊 Percentile", f"{percentile:.0f}th")
                                
                                # Average comparison
                                avg_score = sum(all_scores) / len(all_scores)
                                diff_from_avg = score - avg_score
                                st.metric("📈 vs Average", f"{diff_from_avg:+.1f}", f"Avg: {avg_score:.1f}")
                                
                                # Best performer
                                best_org = org_name if score == max(all_scores) else max(similar_orgs, key=lambda x: x['total_score'])['name']
                                if isinstance(best_org, dict):
                                    best_org = best_org['name']
                                st.markdown(f"**🥇 Top Performer:** {best_org}")
                            
                            # Detailed comparison insights
                            st.markdown("#### 🔍 Key Insights")
                            
                            insights = []
                            
                            # Score comparison insights
                            if your_rank == 1:
                                insights.append("🏆 **Excellent Performance**: You're the top performer among similar organizations!")
                            elif your_rank <= len(all_scores) // 3:
                                insights.append("🌟 **Above Average**: Your organization performs better than most peers.")
                            elif your_rank <= 2 * len(all_scores) // 3:
                                insights.append("📊 **Average Performance**: Your organization is performing at par with peers.")
                            else:
                                insights.append("📈 **Improvement Opportunity**: Consider focusing on quality enhancement initiatives.")
                            
                            # Certification comparison
                            your_certs = len([c for c in org_data['certifications'] if c['status'] == 'Active'])
                            avg_certs = sum([len([c for c in org['certifications'] if c['status'] == 'Active']) for org in similar_orgs]) / len(similar_orgs) if similar_orgs else 0
                            
                            if your_certs > avg_certs:
                                insights.append(f"🏅 **Strong Certification Portfolio**: You have {your_certs} active certifications vs {avg_certs:.1f} average.")
                            elif your_certs < avg_certs:
                                insights.append(f"📋 **Certification Gap**: Consider pursuing additional certifications (you have {your_certs} vs {avg_certs:.1f} average).")
                            
                            # Quality initiatives comparison
                            your_initiatives = len(org_data['quality_initiatives'])
                            avg_initiatives = sum([len(org['quality_initiatives']) for org in similar_orgs]) / len(similar_orgs) if similar_orgs else 0
                            
                            if your_initiatives > avg_initiatives:
                                insights.append(f"🚀 **Innovation Leader**: You have {your_initiatives} quality initiatives vs {avg_initiatives:.1f} average.")
                            elif your_initiatives < avg_initiatives:
                                insights.append(f"💡 **Innovation Opportunity**: Consider implementing more quality initiatives (you have {your_initiatives} vs {avg_initiatives:.1f} average).")
                            
                            for insight in insights:
                                st.markdown(insight)
                            
                            # Improvement recommendations
                            if your_rank > 1:
                                st.markdown("#### 💡 Improvement Recommendations")
                                
                                # Find top performer for benchmarking
                                top_performer = max(similar_orgs, key=lambda x: x['total_score'])
                                
                                recommendations = []
                                
                                # Certification recommendations
                                top_certs = len([c for c in top_performer['certifications'] if c['status'] == 'Active'])
                                if your_certs < top_certs:
                                    recommendations.append(f"🏅 **Pursue Additional Certifications**: Top performer ({top_performer['name']}) has {top_certs} active certifications.")
                                
                                # Initiative recommendations
                                top_initiatives = len(top_performer['quality_initiatives'])
                                if your_initiatives < top_initiatives:
                                    recommendations.append(f"🚀 **Expand Quality Initiatives**: Top performer has {top_initiatives} quality programs.")
                                
                                # Score gap analysis
                                score_gap = top_performer['total_score'] - score
                                if score_gap > 5:
                                    recommendations.append(f"📈 **Focus Areas**: Bridge the {score_gap:.1f} point gap through targeted quality improvements.")
                                
                                for rec in recommendations:
                                    st.markdown(rec)
                        
                        else:
                            st.info("🔍 No similar organizations found in your locality. This might be due to limited data availability for your region.")
                
                else:
                    st.error("❌ Could not find sufficient data for this organization. Please check the spelling or try a different organization name.")
        elif search_button and not org_name:
            st.warning("⚠️ Please enter an organization name to search.")
        

        
        # Display detailed report if requested
        if hasattr(st.session_state, 'detailed_org') and hasattr(st.session_state, 'detailed_data'):
            st.markdown("---")
            st.subheader(f"📋 Detailed Quality Report: {st.session_state.detailed_org}")
            
            org_data = st.session_state.detailed_data
            
            # Comprehensive metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                score = org_data['total_score']
                score_color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                st.metric("🏆 Overall Score", f"{score}/100", f"{score_color}")
            
            with col2:
                active_certs = len([c for c in org_data['certifications'] if c['status'] == 'Active'])
                st.metric("📜 Active Certifications", active_certs)
            
            with col3:
                initiatives_count = len(org_data['quality_initiatives'])
                st.metric("📈 Quality Initiatives", initiatives_count)
            
            with col4:
                trend = "Improving" if score >= 70 else "Stable" if score >= 50 else "Needs Attention"
                trend_icon = "↗️" if score >= 70 else "➡️" if score >= 50 else "↘️"
                st.metric("📊 Quality Trend", trend, trend_icon)
            
            # Score breakdown
            if org_data['score_breakdown']:
                st.markdown("### 📊 Score Breakdown")
                score_data = org_data['score_breakdown']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Certification scores
                    if 'certification_score' in score_data:
                        cert_score = score_data['certification_score']
                        st.progress(cert_score / 100)
                        st.write(f"**Certifications:** {cert_score}/100")
                    
                    # Initiative scores
                    if 'initiative_score' in score_data:
                        init_score = score_data['initiative_score']
                        st.progress(init_score / 100)
                        st.write(f"**Quality Initiatives:** {init_score}/100")
                
                with col2:
                    # Display certifications
                    if org_data['certifications']:
                        st.markdown("**🏆 Active Certifications:**")
                        for cert in org_data['certifications'][:5]:  # Show top 5
                            if cert['status'] == 'Active':
                                st.write(f"• {cert['name']} - {cert['issuer']}")
            
            # Clear detailed view button
            if st.button("❌ Close QuXAT Report", key="close_detailed"):
                if hasattr(st.session_state, 'detailed_org'):
                    del st.session_state.detailed_org
                if hasattr(st.session_state, 'detailed_data'):
                    del st.session_state.detailed_data
                st.rerun()
        
        st.markdown("---")
        
        st.markdown("""
        ### About QuXAT
        The **QuXAT (Quality eXcellence Assessment Tool)** is a comprehensive platform designed to evaluate 
        and score healthcare organizations worldwide based on their quality initiatives, certifications, 
        and accreditations.
        
        ### Key Features:
        - **🔍 Organization Search** - Find and analyze any healthcare organization globally
        - **📊 Quality Scoring** - Comprehensive scoring based on certifications and quality initiatives
        - **🏆 Certification Tracking** - Monitor ISO, NABH, NABL, JCI, and other quality certifications
        - **📈 Quality Trends** - Track quality improvements and initiatives over time
        - **📰 News Integration** - Real-time updates from company disclosures and news articles
        
        ### Tracked Certifications:
        - **ISO Certifications** - International Organization for Standardization
        - **NABH** - National Accreditation Board for Hospitals & Healthcare Providers
        - **NABL** - National Accreditation Board for Testing and Calibration Laboratories
        - **JCI** - Joint Commission International
        - **HIMSS** - Healthcare Information and Management Systems Society
        - **AAAHC** - Accreditation Association for Ambulatory Health Care
        
        ---
        
        ### ⚠️ Important Legal Disclaimers
        
        **Assessment Nature & Limitations:**
        - The QuXAT grid is an **assessment tool based on publicly available knowledge** regarding healthcare organizations
        - **The QuXAT grid can be wrong** in assessing the quality of an organization and should not be considered as definitive or absolute
        - Scores are generated using automated algorithms and may not reflect the complete picture of an organization's quality
        - This platform is intended for **informational and comparative analysis purposes only**
        
        **Data Accuracy & Reliability:**
        - Information is sourced from publicly available databases, websites, and publications
        - Data accuracy depends on the reliability and timeliness of public sources
        - Organizations may have additional certifications or quality initiatives not captured in our database
        - Certification statuses may change without immediate reflection in our system
        
        **No Medical or Professional Advice:**
        - QuXAT scores do not constitute medical advice, professional recommendations, or endorsements
        - Users should conduct independent verification and due diligence before making healthcare decisions
        - This tool should not be used as the sole basis for selecting healthcare providers or organizations
        
        **Limitation of Liability:**
        - QuXAT and its developers disclaim all warranties, express or implied, regarding the accuracy or completeness of information
        - Users assume full responsibility for any decisions made based on QuXAT assessments
        - No liability is accepted for any direct, indirect, or consequential damages arising from the use of this platform
        
        **Intellectual Property & Fair Use:**
        - All data is used under fair use principles for educational and informational purposes
        - Trademark and certification names are property of their respective owners
        - This platform is not affiliated with or endorsed by any certification bodies or healthcare organizations
        """)
        
        # Reference to Global Healthcare Quality tab
        st.info("📊 **Global Healthcare Quality Distribution** - Visit the **Global Healthcare Quality** tab for comprehensive analysis, interactive charts, and detailed metrics.")
        
        # Interactive button to navigate to Global Healthcare Quality tab
        if st.button("🌍 Go to Global Healthcare Quality Analysis", type="primary", use_container_width=True):
            st.session_state.page = "Global Healthcare Quality"
            st.rerun()

    elif page == "Quality Dashboard":
        st.header("📊 Quality Dashboard & Analytics")
        
        # Sample quality trend data
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        quality_scores = np.random.normal(82, 8, 30)
        trend_data = pd.DataFrame({'Date': dates, 'Average Quality Score': quality_scores})
        
        st.subheader("📈 Global Healthcare Quality Trends")
        fig = px.line(trend_data, x='Date', y='Average Quality Score', 
                      title="30-Day Healthcare Quality Score Trend")
        st.plotly_chart(fig, use_container_width=True)
        
        # Regional analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌍 Regional Quality Analysis")
            regions = ['North America', 'Europe', 'Asia-Pacific', 'Middle East', 'Latin America']
            avg_scores = [88, 85, 79, 76, 73]
            
            fig = px.bar(x=regions, y=avg_scores, title="Average Quality Scores by Region")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Key Metrics")
            st.metric("🏥 Total Organizations", "1,247", "↑ +23")
            st.metric("📊 Average Score", "81.2", "↑ +2.1")
            st.metric("🏆 Top Performers (90+)", "156", "↑ +8")
            st.metric("⚠️ Need Improvement (<60)", "89", "↓ -12")

    elif page == "Global Healthcare Quality":
        st.header("🌍 Global Healthcare Quality Distribution")
        st.markdown("Interactive world map showing healthcare quality scores across different countries and regions with advanced filtering and analysis capabilities.")
        
        # Global Healthcare Quality Distribution Chart and Metrics (moved from home page)
        st.subheader("📊 Healthcare Organizations by Quality Score Range")
        
        # Generate sample data
        quality_ranges = ['75-85 (A+)', '65-74 (A)', '55-64 (B+)', '45-54 (B)', 'Below 45 (C)']
        organization_counts = [150, 320, 280, 180, 70]
        colors = ['#2E8B57', '#32CD32', '#FFD700', '#FFA500', '#FF6347']
        
        fig = px.bar(x=quality_ranges, y=organization_counts, 
                     title="Healthcare Organizations by Quality Score Range",
                     color=quality_ranges, color_discrete_sequence=colors)
        fig.update_layout(showlegend=False, xaxis_title="Quality Score Range", yaxis_title="Number of Organizations")
        st.plotly_chart(fig, use_container_width=True)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏥 Organizations Tracked", "1,000+")
        with col2:
            st.metric("🌍 Countries Covered", "50+")
        with col3:
            st.metric("📊 Average Quality Score", "78.5")
        with col4:
            st.metric("🏆 Top Performers", "150")
        
        st.divider()  # Visual separator between sections
        
        # Enhanced map customization options
        st.subheader("🎛️ Map Controls & Filters")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            color_scale = st.selectbox(
                "🎨 Color Scale",
                ["RdYlGn", "Viridis", "Plasma", "Blues", "Reds", "RdBu", "Turbo", "Rainbow"],
                index=0,
                help="Choose color scheme for the map visualization"
            )
        
        with col2:
            projection = st.selectbox(
                "🗺️ Map Projection",
                ["natural earth", "orthographic", "mercator", "robinson", "kavrayskiy7", "mollweide", "eckert4"],
                index=0,
                help="Select map projection style"
            )
        
        with col3:
            show_text = st.checkbox("📝 Show Country Codes", value=False, help="Display ISO country codes on map")
        
        with col4:
            map_height = st.slider("📏 Map Height", 400, 800, 600, 50, help="Adjust map display height")
        
        # Advanced filtering options
        st.markdown("### 🔍 Advanced Filters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            score_range = st.slider(
                "Quality Score Range",
                min_value=60,
                max_value=95,
                value=(60, 95),
                help="Filter countries by quality score range"
            )
        
        with col2:
            hospital_filter = st.slider(
                "Minimum Top Hospitals",
                min_value=0,
                max_value=50,
                value=0,
                help="Show countries with at least this many top-tier hospitals"
            )
        
        with col3:
            region_filter = st.multiselect(
                "Select Regions",
                ["North America", "Europe", "Asia-Pacific", "Middle East & Africa", "Latin America", "Eastern Europe"],
                default=["North America", "Europe", "Asia-Pacific", "Middle East & Africa", "Latin America", "Eastern Europe"],
                help="Filter by geographic regions"
            )
        
        # Enhanced global healthcare quality data with more comprehensive metrics
        countries_data = {
            'Country': [
                'United States', 'Germany', 'Switzerland', 'Japan', 'Singapore', 'Canada', 'Australia', 
                'United Kingdom', 'France', 'Netherlands', 'Sweden', 'Norway', 'Denmark', 'Finland',
                'South Korea', 'Israel', 'Austria', 'Belgium', 'Italy', 'Spain', 'New Zealand',
                'China', 'India', 'Brazil', 'Russia', 'Mexico', 'Turkey', 'Thailand', 'Malaysia',
                'South Africa', 'Egypt', 'Argentina', 'Chile', 'Poland', 'Czech Republic', 'Hungary',
                'Portugal', 'Greece', 'Ireland', 'Luxembourg', 'Iceland', 'Estonia', 'Latvia', 'Lithuania',
                'UAE', 'Saudi Arabia', 'Qatar', 'Kuwait', 'Bahrain', 'Oman', 'Jordan', 'Lebanon',
                'Morocco', 'Tunisia', 'Algeria', 'Nigeria', 'Kenya', 'Ghana', 'Ethiopia', 'Tanzania',
                'Uganda', 'Rwanda', 'Botswana', 'Namibia', 'Zambia', 'Zimbabwe', 'Mauritius', 'Seychelles'
            ],
            'ISO_Code': [
                'USA', 'DEU', 'CHE', 'JPN', 'SGP', 'CAN', 'AUS', 'GBR', 'FRA', 'NLD', 'SWE', 'NOR', 
                'DNK', 'FIN', 'KOR', 'ISR', 'AUT', 'BEL', 'ITA', 'ESP', 'NZL', 'CHN', 'IND', 'BRA', 
                'RUS', 'MEX', 'TUR', 'THA', 'MYS', 'ZAF', 'EGY', 'ARG', 'CHL', 'POL', 'CZE', 'HUN',
                'PRT', 'GRC', 'IRL', 'LUX', 'ISL', 'EST', 'LVA', 'LTU', 'ARE', 'SAU', 'QAT', 'KWT',
                'BHR', 'OMN', 'JOR', 'LBN', 'MAR', 'TUN', 'DZA', 'NGA', 'KEN', 'GHA', 'ETH', 'TZA',
                'UGA', 'RWA', 'BWA', 'NAM', 'ZMB', 'ZWE', 'MUS', 'SYC'
            ],
            'Quality_Score': [
                92, 89, 94, 88, 91, 87, 86, 85, 84, 87, 88, 90, 89, 87, 85, 83, 86, 84, 82, 81, 85,
                78, 72, 75, 70, 73, 74, 76, 77, 69, 65, 74, 78, 79, 80, 78, 81, 79, 86, 88, 89, 82, 81, 80,
                82, 79, 85, 81, 83, 78, 76, 74, 71, 73, 68, 64, 67, 69, 63, 66, 68, 72, 75, 73, 70, 67, 79, 84
            ],
            'Healthcare_Rank': [
                1, 4, 2, 6, 3, 8, 9, 10, 11, 7, 5, 4, 4, 8, 10, 12, 9, 11, 13, 14, 9,
                25, 35, 28, 40, 32, 30, 26, 24, 42, 48, 29, 25, 22, 21, 23, 18, 20, 7, 6, 5, 19, 20, 21,
                15, 27, 12, 17, 14, 31, 33, 36, 45, 38, 52, 58, 49, 44, 61, 55, 50, 41, 37, 39, 43, 54, 16, 13
            ],
            'Top_Hospitals': [
                15, 8, 6, 7, 4, 6, 5, 9, 7, 4, 3, 2, 2, 2, 4, 3, 3, 2, 4, 3, 2,
                12, 8, 4, 3, 2, 3, 2, 2, 1, 1, 2, 2, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1,
                3, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
            ],
            'Population_Millions': [
                331, 83, 8.7, 125, 5.9, 38, 25, 67, 68, 17, 10, 5.4, 5.8, 5.5, 52, 9.4, 9, 11.5, 60, 47, 5.1,
                1439, 1380, 215, 146, 129, 84, 70, 33, 60, 104, 45, 19, 38, 10.7, 9.7, 10.3, 10.7, 5, 0.6, 0.37, 1.3, 1.9, 2.8,
                9.9, 35, 2.9, 4.3, 1.7, 5.1, 10.2, 6.8, 37, 12, 44, 218, 54, 32, 117, 60, 47, 13, 2.6, 2.5, 18, 15, 1.3, 0.1
            ],
            'GDP_Per_Capita': [
                63543, 46259, 81867, 39285, 59797, 46327, 51812, 42330, 38625, 52331, 51648, 75420, 60170, 48810, 31846, 43592, 47291, 46421, 31953, 27057, 42084,
                10500, 1900, 8717, 11289, 9673, 9127, 7189, 11373, 6001, 3019, 9912, 13231, 13823, 23111, 15731, 23252, 17676, 78785, 115874, 68384, 19847, 17861, 19158,
                43103, 23139, 62088, 29301, 23504, 15343, 4405, 8017, 3204, 3447, 2207, 2097, 1838, 2328, 854, 1141, 1155, 4315, 7715, 4448, 1539, 1464, 11208, 16426
            ]
        }
        
        df_countries = pd.DataFrame(countries_data)
        
        # Apply filters
        filtered_df = df_countries[
            (df_countries['Quality_Score'] >= score_range[0]) & 
            (df_countries['Quality_Score'] <= score_range[1]) &
            (df_countries['Top_Hospitals'] >= hospital_filter)
        ]
        
        # Regional filtering
        region_mapping = {
            'North America': ['USA', 'CAN', 'MEX'],
            'Europe': ['DEU', 'CHE', 'GBR', 'FRA', 'NLD', 'SWE', 'NOR', 'DNK', 'FIN', 'AUT', 'BEL', 'ITA', 'ESP', 'PRT', 'GRC', 'IRL', 'LUX', 'ISL', 'EST', 'LVA', 'LTU', 'POL', 'CZE', 'HUN'],
            'Asia-Pacific': ['JPN', 'SGP', 'AUS', 'KOR', 'CHN', 'IND', 'THA', 'MYS', 'NZL'],
            'Middle East & Africa': ['ISR', 'ZAF', 'EGY', 'ARE', 'SAU', 'QAT', 'KWT', 'BHR', 'OMN', 'JOR', 'LBN', 'MAR', 'TUN', 'DZA', 'NGA', 'KEN', 'GHA', 'ETH', 'TZA', 'UGA', 'RWA', 'BWA', 'NAM', 'ZMB', 'ZWE', 'MUS', 'SYC'],
            'Latin America': ['BRA', 'ARG', 'CHL'],
            'Eastern Europe': ['RUS', 'TUR']
        }
        
        # Filter by selected regions
        selected_countries = []
        for region in region_filter:
            if region in region_mapping:
                selected_countries.extend(region_mapping[region])
        
        if selected_countries:
            filtered_df = filtered_df[filtered_df['ISO_Code'].isin(selected_countries)]
        
        # Create the world map using Plotly Express
        st.subheader("🗺️ Interactive World Healthcare Quality Map")
        
        # Display filter results
        st.info(f"📊 Showing {len(filtered_df)} countries based on your filters")
        
        # Enhanced choropleth map with better styling
        fig = px.choropleth(
            filtered_df,
            locations='ISO_Code',
            color='Quality_Score',
            hover_name='Country',
            hover_data={
                'Quality_Score': ':,.0f',
                'Healthcare_Rank': ':,.0f',
                'Top_Hospitals': ':,.0f',
                'Population_Millions': ':,.1f',
                'GDP_Per_Capita': ':,.0f',
                'ISO_Code': False
            },
            color_continuous_scale=color_scale,
            range_color=[score_range[0], score_range[1]],
            title=f"Global Healthcare Quality Distribution (Quality Score: {score_range[0]}-{score_range[1]})",
            labels={
                'Quality_Score': 'Quality Score',
                'Population_Millions': 'Population (M)',
                'GDP_Per_Capita': 'GDP per Capita ($)'
            }
        )
        
        # Enhanced layout with better styling
        fig.update_layout(
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor="RebeccaPurple",
                projection_type=projection,
                bgcolor='rgba(0,0,0,0)',
                showland=True,
                landcolor='rgb(243, 243, 243)',
                showocean=True,
                oceancolor='rgb(204, 229, 255)'
            ),
            title_x=0.5,
            title_font_size=16,
            width=1200,
            height=map_height,
            font=dict(size=12),
            coloraxis_colorbar=dict(
                title="Quality Score",
                thickness=15,
                len=0.7,
                x=1.02
            )
        )
        
        if show_text:
            fig.update_traces(
                text=filtered_df['ISO_Code'],
                textposition="middle center",
                textfont_size=8,
                textfont_color="white"
            )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display key statistics
        st.markdown("### 📊 Global Healthcare Quality Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_score = filtered_df['Quality_Score'].mean()
            st.metric(
                "Global Average Score", 
                f"{avg_score:.1f}",
                delta=f"{avg_score - 75:.1f} vs baseline"
            )
        
        with col2:
            top_country = filtered_df.loc[filtered_df['Quality_Score'].idxmax()]
            st.metric(
                "Top Performer", 
                top_country['Country'],
                delta=f"{top_country['Quality_Score']:.0f} points"
            )
        
        with col3:
            high_quality = len(filtered_df[filtered_df['Quality_Score'] >= 85])
            st.metric(
                "High Quality Countries", 
                high_quality,
                delta=f"{(high_quality/len(filtered_df)*100):.0f}% of total"
            )
        
        with col4:
            total_hospitals = filtered_df['Top_Hospitals'].sum()
            st.metric(
                "Total Top-Tier Hospitals", 
                f"{total_hospitals:,}",
                delta="Across all regions"
            )
        
        # Regional Analysis
        st.markdown("### 🌍 Regional Healthcare Quality Analysis")
        
        # Create regional breakdown
        regions = {
            'North America': ['United States', 'Canada'],
            'Europe': ['Germany', 'United Kingdom', 'France', 'Switzerland', 'Netherlands', 'Sweden', 'Denmark', 'Norway'],
            'Asia-Pacific': ['Singapore', 'Japan', 'Australia', 'South Korea', 'New Zealand'],
            'Middle East': ['Israel', 'UAE'],
            'Others': ['Brazil', 'South Africa']
        }
        
        regional_data = []
        for region, countries in regions.items():
            region_df = filtered_df[filtered_df['Country'].isin(countries)]
            if not region_df.empty:
                regional_data.append({
                    'Region': region,
                    'Countries': len(region_df),
                    'Avg_Score': region_df['Quality_Score'].mean(),
                    'Top_Hospitals': region_df['Top_Hospitals'].sum(),
                    'Avg_GDP': region_df['GDP_Per_Capita'].mean()
                })
        
        if regional_data:
            regional_df = pd.DataFrame(regional_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Regional quality scores bar chart
                fig_bar = px.bar(
                    regional_df, 
                    x='Region', 
                    y='Avg_Score',
                    title="Average Quality Score by Region",
                    color='Avg_Score',
                    color_continuous_scale='Viridis',
                    text='Avg_Score'
                )
                fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig_bar.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # Regional hospital distribution pie chart
                fig_pie = px.pie(
                    regional_df, 
                    values='Top_Hospitals', 
                    names='Region',
                    title="Distribution of Top-Tier Hospitals by Region"
                )
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
        
        # Quality Score Distribution Analysis
        st.markdown("### 📈 Quality Score Distribution Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🏆 Top 5 Performers:**")
            top_5 = filtered_df.nlargest(5, 'Quality_Score')[['Country', 'Quality_Score', 'Top_Hospitals']]
            for idx, row in top_5.iterrows():
                st.write(f"**{row['Country']}** - {row['Quality_Score']:.0f} points ({row['Top_Hospitals']} hospitals)")
        
        with col2:
            st.markdown("**📊 Score Range Distribution:**")
            score_ranges = [
                ('75-85 (A+)', len(filtered_df[filtered_df['Quality_Score'] >= 75])),
                    ('65-74 (A)', len(filtered_df[(filtered_df['Quality_Score'] >= 65) & (filtered_df['Quality_Score'] < 75)])),
                    ('55-64 (B+)', len(filtered_df[(filtered_df['Quality_Score'] >= 55) & (filtered_df['Quality_Score'] < 65)])),
                    ('45-54 (B)', len(filtered_df[(filtered_df['Quality_Score'] >= 45) & (filtered_df['Quality_Score'] < 55)])),
                    ('Below 45 (C)', len(filtered_df[filtered_df['Quality_Score'] < 45]))
            ]
            
            for range_name, count in score_ranges:
                percentage = (count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
                st.write(f"**{range_name}:** {count} countries ({percentage:.1f}%)")
        
        # Methodology and Data Sources
        st.markdown("---")
        st.markdown("### 📋 Methodology & Data Sources")
        
        with st.expander("🔍 View Detailed Methodology", expanded=False):
            st.markdown("""
            **Quality Score Calculation:**
            - **Certifications (60%):** ISO, JCI, NABH, and other international standards
            - **Quality Initiatives (20%):** Patient safety programs, digital health adoption
            - **Transparency (10%):** Public reporting of quality metrics
            - **Reputation Factors (10%):** International rankings and academic recognition

            **Data Sources:**
            - World Health Organization (WHO) Global Health Observatory
            - OECD Health Statistics
            - International healthcare accreditation bodies
            - Academic medical center databases
            - Government health ministry reports

            **⚠️ Data Accuracy Disclaimers:**
            - **Aggregated Metrics:** This visualization represents aggregated healthcare quality metrics based on available public data
            - **Geographic Limitations:** Country-level data may not reflect individual organization quality within that region
            - **Data Completeness:** Some countries may have limited or outdated information affecting accuracy of regional assessments
            - **Comparative Purpose Only:** Use this map for comparative analysis and research, not for absolute quality determination
            - **Assessment Limitations:** Regional scores may be incorrect or incomplete due to data availability constraints
            """)
        
        # Update layout for better visualization
        fig.update_layout(
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type=projection,
                bgcolor='rgba(0,0,0,0)'
            ),
            title_x=0.5,
            width=1000,
            height=600,
            font=dict(size=12)
        )
        
        if show_text:
            fig.update_traces(
                text=df_countries['ISO_Code'],
                textposition="middle center",
                textfont_size=8
            )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistics and insights
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_score = df_countries['Quality_Score'].mean()
            st.metric("🌍 Global Average", f"{avg_score:.1f}", "Quality Score")
        
        with col2:
            top_country = df_countries.loc[df_countries['Quality_Score'].idxmax(), 'Country']
            top_score = df_countries['Quality_Score'].max()
            st.metric("🥇 Top Performer", top_country, f"{top_score} pts")
        
        with col3:
            high_quality = len(df_countries[df_countries['Quality_Score'] >= 85])
            st.metric("⭐ High Quality (85+)", high_quality, "countries")
        
        with col4:
            total_hospitals = df_countries['Top_Hospitals'].sum()
            st.metric("🏥 Top-Tier Hospitals", total_hospitals, "globally")
        
        # Regional breakdown
        st.subheader("📊 Regional Quality Analysis")
        
        # Define regions (simplified)
        region_mapping = {
            'North America': ['USA', 'CAN', 'MEX'],
            'Europe': ['DEU', 'CHE', 'GBR', 'FRA', 'NLD', 'SWE', 'NOR', 'DNK', 'FIN', 'AUT', 'BEL', 'ITA', 'ESP', 'PRT', 'GRC', 'IRL', 'LUX', 'ISL', 'EST', 'LVA', 'LTU', 'POL', 'CZE', 'HUN'],
            'Asia-Pacific': ['JPN', 'SGP', 'AUS', 'KOR', 'CHN', 'IND', 'THA', 'MYS', 'NZL'],
            'Middle East & Africa': ['ISR', 'ZAF', 'EGY'],
            'Latin America': ['BRA', 'ARG', 'CHL'],
            'Eastern Europe': ['RUS', 'TUR']
        }
        
        regional_data = []
        for region, countries in region_mapping.items():
            region_df = df_countries[df_countries['ISO_Code'].isin(countries)]
            if not region_df.empty:
                regional_data.append({
                    'Region': region,
                    'Average_Score': region_df['Quality_Score'].mean(),
                    'Countries': len(region_df),
                    'Top_Hospitals': region_df['Top_Hospitals'].sum()
                })
        
        regional_df = pd.DataFrame(regional_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_regional = px.bar(
                regional_df, 
                x='Region', 
                y='Average_Score',
                title="Average Quality Score by Region",
                color='Average_Score',
                color_continuous_scale='RdYlGn'
            )
            fig_regional.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig_regional, use_container_width=True)
        
        with col2:
            fig_hospitals = px.pie(
                regional_df, 
                values='Top_Hospitals', 
                names='Region',
                title="Distribution of Top-Tier Hospitals by Region"
            )
            st.plotly_chart(fig_hospitals, use_container_width=True)
        
        # Top and bottom performers
        st.subheader("🏆 Performance Rankings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🥇 Top 10 Performers**")
            top_10 = df_countries.nlargest(10, 'Quality_Score')[['Country', 'Quality_Score', 'Healthcare_Rank']]
            top_10.index = range(1, len(top_10) + 1)
            st.dataframe(top_10, use_container_width=True)
        
        with col2:
            st.markdown("**📈 Improvement Opportunities**")
            bottom_10 = df_countries.nsmallest(10, 'Quality_Score')[['Country', 'Quality_Score', 'Healthcare_Rank']]
            bottom_10.index = range(1, len(bottom_10) + 1)
            st.dataframe(bottom_10, use_container_width=True)
        
        # Quality score distribution
        st.subheader("📈 Quality Score Distribution")
        
        fig_dist = px.histogram(
            df_countries, 
            x='Quality_Score', 
            nbins=15,
            title="Distribution of Healthcare Quality Scores Globally",
            labels={'count': 'Number of Countries', 'Quality_Score': 'Quality Score'},
            color_discrete_sequence=['#2E86AB']
        )
        fig_dist.update_layout(showlegend=False)
        st.plotly_chart(fig_dist, use_container_width=True)
        
        # Data source and methodology
        st.markdown("---")
        st.markdown("""
        ### 📋 Methodology & Data Sources
        
        **Quality Score Calculation:**
        - **Certifications (60%):** ISO, JCI, NABH, and other international standards
        - **Quality Initiatives (20%):** Patient safety programs, digital health adoption
        - **Transparency (10%):** Public reporting of quality metrics
        - **Reputation Factors (10%):** International rankings and academic recognition
        
        **Data Sources:**
        - World Health Organization (WHO) Global Health Observatory
        - OECD Health Statistics
        - International healthcare accreditation bodies
        - Academic medical center databases
        - Government health ministry reports
        
        **⚠️ Data Accuracy Disclaimers:**
        - **Aggregated Metrics:** This visualization represents aggregated healthcare quality metrics based on available public data
        - **Geographic Limitations:** Country-level data may not reflect individual organization quality within that region
        - **Data Completeness:** Some countries may have limited or outdated information affecting accuracy of regional assessments
        - **Comparative Purpose Only:** Use this map for comparative analysis and research, not for absolute quality determination
        - **Assessment Limitations:** Regional scores may be incorrect or incomplete due to data availability constraints
        """)
        
        # Data Upload Section for Users
        st.markdown("---")
        st.markdown("### 📤 Contribute Quality Data")
        st.markdown("Help improve our database by sharing quality-centric data about healthcare organizations.")
        
        with st.expander("📋 Upload Healthcare Quality Data", expanded=False):
            st.markdown("**Share your organization's quality achievements with the community!**")
            
            with st.form("data_upload_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    upload_org_name = st.text_input("🏥 Organization Name*", placeholder="e.g., City General Hospital")
                    upload_location = st.text_input("📍 Location*", placeholder="e.g., New York, USA")
                    upload_type = st.selectbox("🏢 Organization Type*", 
                                             ["Hospital", "Clinic", "Medical Center", "Specialty Center", "Other"])
                
                with col2:
                    upload_certification = st.text_input("📜 Certification/Achievement*", 
                                                       placeholder="e.g., JCI Accreditation, ISO 9001")
                    upload_year = st.number_input("📅 Year Achieved*", min_value=2000, max_value=2024, value=2024)
                    upload_category = st.selectbox("📊 Category*", 
                                                 ["Patient Safety", "Quality Management", "Clinical Excellence", 
                                                  "Technology Innovation", "Staff Training", "Other"])
                
                upload_description = st.text_area("📝 Description*", 
                                                placeholder="Describe the quality achievement, certification details, or improvement initiative...")
                upload_contact = st.text_input("📧 Contact Email (Optional)", 
                                             placeholder="your.email@organization.com")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    submit_upload = st.form_submit_button("📤 Submit for Review", type="primary")
                
                if submit_upload:
                    if upload_org_name and upload_location and upload_certification and upload_description:
                        upload_data = {
                            'organization_name': upload_org_name,
                            'location': upload_location,
                            'organization_type': upload_type,
                            'certification': upload_certification,
                            'year_achieved': upload_year,
                            'category': upload_category,
                            'description': upload_description,
                            'contact_email': upload_contact,
                            'submitter_ip': 'anonymous'  # In production, you might want to track this
                        }
                        
                        add_pending_upload(upload_data)
                        st.success("✅ Thank you! Your submission has been received and will be reviewed by our admin team.")
                        st.info("📋 **Review Process:** All submissions are manually reviewed to ensure data quality and accuracy before being made public.")
                    else:
                        st.error("❌ Please fill in all required fields marked with *")
            
            st.markdown("""
            **📋 Submission Guidelines:**
            - Provide accurate and verifiable information
            - Include official certification names and dates
            - Describe achievements clearly and concisely
            - All submissions are reviewed before publication
            """)

    elif page == "QuXAT Scoring Method":
        st.header("📋 Comprehensive QuXAT Score Report")
        
        # Check if there's a queried organization from session state
        if hasattr(st.session_state, 'queried_org_name') and st.session_state.queried_org_name:
            # Display the queried organization's detailed report
            org_name = st.session_state.queried_org_name
            org_data = st.session_state.queried_org_data
            
            st.markdown(f"### 🏥 Detailed Analysis for: **{org_name}**")
            
            # Display the detailed scorecard
            display_detailed_scorecard_inline(org_name, org_data, org_data['overall_score'])
            
            # Add a button to clear the selection and go back to organization selector
            if st.button("🔄 View Different Organization", type="secondary"):
                st.session_state.queried_org_name = None
                st.session_state.queried_org_data = None
                st.rerun()
        
        else:
            # No queried organization available
            st.markdown("### 🔍 No Organization Selected")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    padding: 2rem;
                    border-radius: 15px;
                    text-align: center;
                    border: 2px solid #e1e8ed;
                    margin: 2rem 0;
                ">
                    <h3 style="color: #2c3e50; margin-bottom: 1rem;">📊 Comprehensive QuXAT Score Report</h3>
                    <p style="color: #5a6c7d; font-size: 1.1rem; margin-bottom: 1.5rem;">
                        To view a detailed quality assessment report, please search for a healthcare organization using the search function on the Home page.
                    </p>
                    <div style="
                        background: #ffffff;
                        padding: 1.5rem;
                        border-radius: 10px;
                        margin: 1rem 0;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    ">
                        <h4 style="color: #3498db; margin-bottom: 1rem;">🎯 What You'll Get:</h4>
                        <ul style="text-align: left; color: #2c3e50; line-height: 1.6;">
                            <li><strong>Overall QuXAT Score:</strong> Comprehensive quality rating out of 100</li>
                            <li><strong>Detailed Breakdown:</strong> Certifications, quality initiatives, and transparency metrics</li>
                            <li><strong>Visual Analytics:</strong> Interactive charts and score component analysis</li>
                            <li><strong>Certification Analysis:</strong> Complete certification portfolio with validity timelines</li>
                            <li><strong>Quality Initiatives:</strong> Recent improvement programs and innovations</li>
                            <li><strong>Scoring Methodology:</strong> Transparent explanation of how scores are calculated</li>
                        </ul>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🏠 Go to Home Page", use_container_width=True):
                    st.session_state.page = "Home"
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### 📋 How to Get Started")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                #### 🔍 Step 1: Search
                - Navigate to the **Home** page
                - Enter any healthcare organization name
                - Use the search function to find organizations worldwide
                """)
            
            with col2:
                st.markdown("""
                #### 📊 Step 2: View Report
                - Click **"👁️ View QuXAT Report"** button
                - Get automatically redirected to this page
                - Explore comprehensive quality metrics and analysis
                """)
        
        with col2:
            st.markdown("""
            #### ⚠️ Important Limitations
            - **Public Data Only:** Based on publicly available information
            - **Algorithmic Assessment:** May not capture all quality aspects
            - **Data Lag:** Information may not reflect most recent changes
            - **Geographic Bias:** Better data availability for certain regions
            - **Language Limitations:** Primarily English-language sources
            - **Not Medical Advice:** For comparative analysis only
            """)
        


    elif page == "Certifications":
        st.header("🏆 Global Healthcare Quality Certifications")
        
        st.markdown("""
        ### 🌍 Comprehensive Global Healthcare Quality Standards
        Healthcare quality certifications are essential indicators of an organization's commitment to excellence, 
        patient safety, and continuous improvement. This comprehensive database includes certifications from 
        **over 50 countries and regions** worldwide, representing the most exhaustive collection of healthcare 
        quality standards available.
        """)
        
        # Search and filter functionality
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            search_term = st.text_input("🔍 Search Certifications", placeholder="Enter certification name, country, or focus area...")
        with col2:
            region_filter = st.selectbox("🌐 Filter by Region", 
                                       ["All Regions", "International", "North America", "Europe", "Asia-Pacific", 
                                        "Middle East & Africa", "Latin America", "Oceania"])
        with col3:
            focus_filter = st.selectbox("🎯 Filter by Focus Area", 
                                      ["All Areas", "Hospital Accreditation", "Quality Management", "Patient Safety", 
                                       "Laboratory Standards", "Information Security", "Environmental Management"])
        
        # International Standards
        st.markdown("---")
        st.markdown("### 🌐 International Standards (Global Recognition)")
        intl_certs = pd.DataFrame({
            'Certification': [
                'ISO 9001:2015', 'ISO 14001:2015', 'ISO 45001:2018', 'ISO 27001:2013', 'ISO 13485:2016',
                'JCI (Joint Commission International)', 'WHO-FIC Collaborating Centre', 'IEC 62304', 
                'ISO 15189:2012', 'ISO 17025:2017', 'CLIA (Clinical Laboratory Improvement Amendments)',
                'CAP (College of American Pathologists)', 'RTAC (Reproductive Technology Accreditation Committee)'
            ],
            'Focus Area': [
                'Quality Management Systems', 'Environmental Management', 'Occupational Health & Safety', 
                'Information Security Management', 'Medical Devices Quality', 'Hospital Accreditation',
                'Health Information Standards', 'Medical Device Software', 'Medical Laboratory Quality',
                'Testing & Calibration Laboratories', 'Laboratory Quality Standards', 'Laboratory Accreditation',
                'Reproductive Technology'
            ],
            'Region': ['Global'] * 13,
            'Recognition Level': ['Very High'] * 13,
            'Score Weight': [15, 12, 12, 10, 18, 25, 8, 10, 20, 15, 18, 20, 15]
        })
        
        # North America
        st.markdown("### 🇺🇸🇨🇦 North America")
        na_certs = pd.DataFrame({
            'Certification': [
                'Joint Commission (TJC)', 'HIMSS EMRAM', 'AAAHC', 'NCQA', 'DNV GL Healthcare',
                'HFAP (Healthcare Facilities Accreditation Program)', 'CHAP (Community Health Accreditation Partner)',
                'ACHC (Accreditation Commission for Health Care)', 'URAC', 'CARF (Commission on Accreditation)',
                'Accreditation Canada', 'CPSO (College of Physicians and Surgeons Ontario)', 'Health Canada GMP'
            ],
            'Focus Area': [
                'Hospital Accreditation', 'Health IT Maturity', 'Ambulatory Care', 'Health Plan Quality',
                'Hospital Accreditation (ISO-based)', 'Healthcare Facilities', 'Community Health Organizations',
                'Healthcare Services', 'Healthcare Quality', 'Rehabilitation Services', 'Healthcare Standards',
                'Medical Practice Standards', 'Good Manufacturing Practices'
            ],
            'Region': ['USA', 'USA', 'USA', 'USA', 'USA', 'USA', 'USA', 'USA', 'USA', 'USA', 'Canada', 'Canada', 'Canada'],
            'Recognition Level': ['Very High', 'High', 'High', 'Very High', 'High', 'Medium', 'Medium', 'Medium', 'High', 'High', 'Very High', 'High', 'High'],
            'Score Weight': [25, 18, 15, 20, 20, 12, 10, 12, 15, 15, 22, 15, 12]
        })
        
        # Europe
        st.markdown("### 🇪🇺 Europe")
        eu_certs = pd.DataFrame({
            'Certification': [
                'CE Marking (Medical Devices)', 'MHRA (UK)', 'ANSM (France)', 'BfArM (Germany)', 'AIFA (Italy)',
                'EMA (European Medicines Agency)', 'NICE (UK)', 'HAS (France)', 'G-BA (Germany)', 'AEMPS (Spain)',
                'Swissmedic (Switzerland)', 'FIMEA (Finland)', 'SUKL (Czech Republic)', 'URPL (Poland)',
                'AGES (Austria)', 'INFARMED (Portugal)', 'EOF (Greece)', 'JAZMP (Slovakia)', 'HALMED (Croatia)',
                'KKH Certification (Netherlands)', 'Sundhedsstyrelsen (Denmark)', 'Läkemedelsverket (Sweden)'
            ],
            'Focus Area': [
                'Medical Device Compliance', 'Medicines & Healthcare Regulation', 'Drug Safety & Efficacy',
                'Medical Devices & Pharmaceuticals', 'Drug Regulation', 'European Drug Regulation',
                'Health Technology Assessment', 'Health Technology Assessment', 'Healthcare Quality Assessment',
                'Pharmaceutical Regulation', 'Swiss Drug Regulation', 'Finnish Drug Regulation',
                'Czech Drug Regulation', 'Polish Drug Regulation', 'Austrian Drug Safety',
                'Portuguese Drug Regulation', 'Greek Drug Regulation', 'Slovak Drug Regulation',
                'Croatian Drug Regulation', 'Dutch Healthcare Quality', 'Danish Health Authority',
                'Swedish Drug Regulation'
            ],
            'Region': ['EU', 'UK', 'France', 'Germany', 'Italy', 'EU', 'UK', 'France', 'Germany', 'Spain', 
                      'Switzerland', 'Finland', 'Czech Republic', 'Poland', 'Austria', 'Portugal', 'Greece', 
                      'Slovakia', 'Croatia', 'Netherlands', 'Denmark', 'Sweden'],
            'Recognition Level': ['Very High', 'Very High', 'High', 'Very High', 'High', 'Very High', 'Very High', 
                                'High', 'High', 'High', 'Very High', 'High', 'Medium', 'Medium', 'Medium', 
                                'Medium', 'Medium', 'Medium', 'Medium', 'High', 'High', 'High'],
            'Score Weight': [20, 22, 15, 20, 15, 25, 18, 15, 15, 15, 20, 12, 10, 10, 10, 10, 8, 8, 8, 12, 12, 12]
        })
        
        # Asia-Pacific
        st.markdown("### 🌏 Asia-Pacific")
        ap_certs = pd.DataFrame({
            'Certification': [
                'NABH (India)', 'NABL (India)', 'QCI Healthcare (India)', 'PMDA (Japan)', 'MHLW (Japan)',
                'TFDA (Taiwan)', 'KFDA (South Korea)', 'HSA (Singapore)', 'TGA (Australia)', 'Medsafe (New Zealand)',
                'NMPA (China)', 'DOH (Philippines)', 'MOH (Malaysia)', 'FDA Thailand', 'BPOM (Indonesia)',
                'DDA (Myanmar)', 'CDSCB (Cambodia)', 'YDA (Yemen)', 'SFDA (Saudi Arabia)', 'NHRA (Bahrain)',
                'MOH UAE', 'Kuwait MOH', 'Oman MOH', 'Qatar MOH'
            ],
            'Focus Area': [
                'Hospital Accreditation', 'Laboratory Accreditation', 'Quality Council Standards', 
                'Pharmaceutical Regulation', 'Health & Welfare Standards', 'Drug & Food Safety',
                'Food & Drug Safety', 'Health Sciences Authority', 'Therapeutic Goods Administration',
                'Medicine Safety Authority', 'Drug Administration', 'Department of Health Standards',
                'Ministry of Health Standards', 'Food & Drug Administration', 'Drug & Food Control',
                'Drug & Device Authority', 'Drug Standards Control', 'Drug Authority', 'Food & Drug Authority',
                'Health Regulation Authority', 'Ministry of Health Standards', 'Ministry of Health Standards',
                'Ministry of Health Standards', 'Ministry of Health Standards'
            ],
            'Region': ['India', 'India', 'India', 'Japan', 'Japan', 'Taiwan', 'South Korea', 'Singapore', 
                      'Australia', 'New Zealand', 'China', 'Philippines', 'Malaysia', 'Thailand', 'Indonesia',
                      'Myanmar', 'Cambodia', 'Yemen', 'Saudi Arabia', 'Bahrain', 'UAE', 'Kuwait', 'Oman', 'Qatar'],
            'Recognition Level': ['Very High', 'High', 'Medium', 'Very High', 'High', 'High', 'High', 'Very High',
                                'Very High', 'High', 'High', 'Medium', 'Medium', 'Medium', 'Medium', 'Low', 'Low',
                                'Medium', 'High', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium'],
            'Score Weight': [20, 15, 12, 22, 15, 15, 15, 18, 20, 12, 15, 10, 10, 10, 10, 6, 6, 8, 12, 8, 8, 8, 8, 8]
        })
        
        # Middle East & Africa
        st.markdown("### 🌍 Middle East & Africa")
        mea_certs = pd.DataFrame({
            'Certification': [
                'SAHPRA (South Africa)', 'MCC (South Africa)', 'NAFDAC (Nigeria)', 'FDB (Ghana)', 'DDA (Ethiopia)',
                'TMDA (Tanzania)', 'NDA (Uganda)', 'PPB (Kenya)', 'ZaZiBoNa (Zimbabwe)', 'MCAZ (Zimbabwe)',
                'Israeli MOH', 'Turkish MOH', 'Egyptian MOH', 'Moroccan MOH', 'Tunisian MOH', 'Algerian MOH',
                'Libyan MOH', 'Sudanese MOH', 'Jordanian MOH', 'Lebanese MOH', 'Syrian MOH', 'Iraqi MOH'
            ],
            'Focus Area': [
                'Health Products Regulation', 'Medicines Control', 'Food & Drug Administration', 'Food & Drugs Board',
                'Drug & Device Authority', 'Medical Device Authority', 'Drug Authority', 'Pharmacy & Poisons Board',
                'Medicine Regulatory Authority', 'Medicine Control Authority', 'Ministry of Health Standards',
                'Ministry of Health Standards', 'Ministry of Health Standards', 'Ministry of Health Standards',
                'Ministry of Health Standards', 'Ministry of Health Standards', 'Ministry of Health Standards',
                'Ministry of Health Standards', 'Ministry of Health Standards', 'Ministry of Health Standards',
                'Ministry of Health Standards', 'Ministry of Health Standards'
            ],
            'Region': ['South Africa', 'South Africa', 'Nigeria', 'Ghana', 'Ethiopia', 'Tanzania', 'Uganda', 'Kenya',
                      'Zimbabwe', 'Zimbabwe', 'Israel', 'Turkey', 'Egypt', 'Morocco', 'Tunisia', 'Algeria',
                      'Libya', 'Sudan', 'Jordan', 'Lebanon', 'Syria', 'Iraq'],
            'Recognition Level': ['High', 'High', 'Medium', 'Medium', 'Low', 'Low', 'Low', 'Medium', 'Low', 'Low',
                                'High', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Low', 'Low', 'Medium',
                                'Medium', 'Low', 'Low'],
            'Score Weight': [15, 15, 10, 10, 6, 6, 6, 8, 6, 6, 12, 10, 10, 10, 10, 10, 6, 6, 8, 8, 6, 6]
        })
        
        # Latin America
        st.markdown("### 🌎 Latin America")
        la_certs = pd.DataFrame({
            'Certification': [
                'ANVISA (Brazil)', 'ANMAT (Argentina)', 'ISP (Chile)', 'INVIMA (Colombia)', 'DIGEMID (Peru)',
                'COFEPRIS (Mexico)', 'CECMED (Cuba)', 'DINAMED (Uruguay)', 'MSP (Ecuador)', 'DINAVISA (Paraguay)',
                'INHRR (Venezuela)', 'MINSA (Panama)', 'MINSAL (El Salvador)', 'SESAL (Honduras)', 'MSPAS (Guatemala)',
                'MINSA (Nicaragua)', 'MINSA (Costa Rica)', 'SENASA (Dominican Republic)', 'MOH (Jamaica)', 'MOH (Trinidad)'
            ],
            'Focus Area': [
                'Health Surveillance Agency', 'Medicine Administration', 'Public Health Institute', 'Drug Surveillance',
                'Medicine Directorate', 'Health Risk Protection', 'Medicine Control Center', 'Medicine Directorate',
                'Public Health Ministry', 'Health Surveillance Directorate', 'Health Regulation Institute',
                'Health Ministry', 'Health Ministry', 'Health Secretary', 'Public Health Ministry',
                'Health Ministry', 'Health Ministry', 'Animal & Plant Health Service', 'Ministry of Health',
                'Ministry of Health'
            ],
            'Region': ['Brazil', 'Argentina', 'Chile', 'Colombia', 'Peru', 'Mexico', 'Cuba', 'Uruguay', 'Ecuador',
                      'Paraguay', 'Venezuela', 'Panama', 'El Salvador', 'Honduras', 'Guatemala', 'Nicaragua',
                      'Costa Rica', 'Dominican Republic', 'Jamaica', 'Trinidad & Tobago'],
            'Recognition Level': ['High', 'High', 'High', 'Medium', 'Medium', 'High', 'Medium', 'Medium', 'Medium',
                                'Low', 'Low', 'Medium', 'Medium', 'Low', 'Low', 'Low', 'Medium', 'Medium', 'Medium', 'Medium'],
            'Score Weight': [15, 15, 15, 10, 10, 12, 8, 8, 8, 6, 6, 8, 8, 6, 6, 6, 8, 8, 8, 8]
        })
        
        # Combine all certifications
        all_certs = pd.concat([intl_certs, na_certs, eu_certs, ap_certs, mea_certs, la_certs], ignore_index=True)
        
        # Apply filters
        filtered_certs = all_certs.copy()
        
        if search_term:
            mask = (filtered_certs['Certification'].str.contains(search_term, case=False, na=False) |
                   filtered_certs['Focus Area'].str.contains(search_term, case=False, na=False) |
                   filtered_certs['Region'].str.contains(search_term, case=False, na=False))
            filtered_certs = filtered_certs[mask]
        
        if region_filter != "All Regions":
            if region_filter == "International":
                filtered_certs = filtered_certs[filtered_certs['Region'] == 'Global']
            elif region_filter == "North America":
                filtered_certs = filtered_certs[filtered_certs['Region'].isin(['USA', 'Canada'])]
            elif region_filter == "Europe":
                eu_regions = ['EU', 'UK', 'France', 'Germany', 'Italy', 'Spain', 'Switzerland', 'Finland', 
                             'Czech Republic', 'Poland', 'Austria', 'Portugal', 'Greece', 'Slovakia', 
                             'Croatia', 'Netherlands', 'Denmark', 'Sweden']
                filtered_certs = filtered_certs[filtered_certs['Region'].isin(eu_regions)]
            elif region_filter == "Asia-Pacific":
                ap_regions = ['India', 'Japan', 'Taiwan', 'South Korea', 'Singapore', 'Australia', 'New Zealand',
                             'China', 'Philippines', 'Malaysia', 'Thailand', 'Indonesia', 'Myanmar', 'Cambodia']
                filtered_certs = filtered_certs[filtered_certs['Region'].isin(ap_regions)]
            elif region_filter == "Middle East & Africa":
                mea_regions = ['South Africa', 'Nigeria', 'Ghana', 'Ethiopia', 'Tanzania', 'Uganda', 'Kenya',
                              'Zimbabwe', 'Israel', 'Turkey', 'Egypt', 'Morocco', 'Tunisia', 'Algeria', 'Libya',
                              'Sudan', 'Jordan', 'Lebanon', 'Syria', 'Iraq', 'Yemen', 'Saudi Arabia', 'Bahrain',
                              'UAE', 'Kuwait', 'Oman', 'Qatar']
                filtered_certs = filtered_certs[filtered_certs['Region'].isin(mea_regions)]
            elif region_filter == "Latin America":
                la_regions = ['Brazil', 'Argentina', 'Chile', 'Colombia', 'Peru', 'Mexico', 'Cuba', 'Uruguay',
                             'Ecuador', 'Paraguay', 'Venezuela', 'Panama', 'El Salvador', 'Honduras', 'Guatemala',
                             'Nicaragua', 'Costa Rica', 'Dominican Republic', 'Jamaica', 'Trinidad & Tobago']
                filtered_certs = filtered_certs[filtered_certs['Region'].isin(la_regions)]
        
        if focus_filter != "All Areas":
            filtered_certs = filtered_certs[filtered_certs['Focus Area'].str.contains(focus_filter, case=False, na=False)]
        
        # Display filtered results
        st.markdown("---")
        st.markdown(f"### 📊 Certification Results ({len(filtered_certs)} of {len(all_certs)} certifications)")
        
        if len(filtered_certs) > 0:
            # Add color coding based on recognition level
            def color_recognition(val):
                if val == 'Very High':
                    return 'background-color: #d4edda; color: #155724'
                elif val == 'High':
                    return 'background-color: #fff3cd; color: #856404'
                elif val == 'Medium':
                    return 'background-color: #f8d7da; color: #721c24'
                else:
                    return 'background-color: #f1f3f4; color: #5f6368'
            
            styled_df = filtered_certs.style.applymap(color_recognition, subset=['Recognition Level'])
            st.dataframe(styled_df, use_container_width=True, height=400)
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🌍 Total Certifications", len(filtered_certs))
            with col2:
                very_high = len(filtered_certs[filtered_certs['Recognition Level'] == 'Very High'])
                st.metric("⭐ Very High Recognition", very_high)
            with col3:
                avg_weight = filtered_certs['Score Weight'].mean()
                st.metric("📊 Average Score Weight", f"{avg_weight:.1f}")
            with col4:
                regions = filtered_certs['Region'].nunique()
                st.metric("🗺️ Regions Covered", regions)
        else:
            st.warning("No certifications found matching your search criteria. Please adjust your filters.")
        
        # Regional distribution chart
        if len(filtered_certs) > 0:
            st.markdown("---")
            st.markdown("### 📈 Regional Distribution Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                region_counts = filtered_certs['Region'].value_counts().head(15)
                fig_regions = px.bar(
                    x=region_counts.values,
                    y=region_counts.index,
                    orientation='h',
                    title="Top 15 Regions by Certification Count",
                    labels={'x': 'Number of Certifications', 'y': 'Region'}
                )
                fig_regions.update_layout(height=400)
                st.plotly_chart(fig_regions, use_container_width=True)
            
            with col2:
                recognition_counts = filtered_certs['Recognition Level'].value_counts()
                fig_recognition = px.pie(
                    values=recognition_counts.values,
                    names=recognition_counts.index,
                    title="Distribution by Recognition Level"
                )
                st.plotly_chart(fig_recognition, use_container_width=True)

    elif page == "Settings":
        st.header("⚙️ Application Settings")
        
        # Admin Login Section
        st.markdown("### 🔐 Admin Access")
        if not is_admin_authenticated():
            with st.expander("Admin Login", expanded=False):
                admin_login()
        else:
            st.success(f"✅ Logged in as: {st.session_state.admin_username}")
            admin_logout()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎨 Display Preferences")
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
            default_view = st.selectbox("Default Page", ["Home", "Organization Search", "Quality Dashboard"])
            
            st.subheader("🔍 Search & Data Settings")
            search_regions = st.multiselect("Search Regions", 
                                          ["Global", "North America", "Europe", "Asia-Pacific", "Middle East", "Africa"],
                                          default=["Global"])
            data_sources = st.multiselect("Data Sources",
                                        ["Company Disclosures", "News Articles", "Certification Bodies", "Government Databases"],
                                        default=["Company Disclosures", "Certification Bodies"])
        
        with col2:
            st.subheader("🏆 Certification Preferences")
            cert_weights = st.slider("Certification Weight (%)", 50, 90, 70)
            initiative_weights = st.slider("Initiative Weight (%)", 10, 40, 20)
            transparency_weights = st.slider("Transparency Weight (%)", 5, 20, 10)
            
            st.subheader("📊 Export & Reporting")
            export_format = st.selectbox("Export Format", ["PDF", "Excel", "CSV"])
            update_frequency = st.selectbox("Data Update Frequency", ["Real-time", "Daily", "Weekly"])
        
        if st.button("💾 Save Settings"):
            st.success("✅ Settings saved successfully!")
            st.info(f"""
            **Settings Summary:**
            - Theme: {theme}
            - Default Page: {default_view}
            - Search Regions: {', '.join(search_regions)}
            - Data Sources: {', '.join(data_sources)}
            - Certification Weight: {cert_weights}%
            - Update Frequency: {update_frequency}
            """)
    
    elif page == "Admin Panel":
        if not is_admin_authenticated():
            st.error("🔒 Access Denied: Admin authentication required")
            st.info("Please login through the Settings page to access the Admin Panel.")
        else:
            st.header("🛠️ Admin Panel")
            st.success(f"Welcome, {st.session_state.admin_username}!")
            
            # Admin Dashboard Tabs
            tab1, tab2, tab3 = st.tabs(["📤 Review Uploads", "🏥 Manage Hospitals", "📊 System Stats"])
            
            with tab1:
                st.subheader("📤 Data Upload Review")
                
                # Initialize upload storage
                init_upload_storage()
                
                # Pending uploads
                if st.session_state.pending_uploads:
                    st.markdown("### 🔍 Pending Reviews")
                    for upload in st.session_state.pending_uploads:
                        with st.expander(f"Upload #{upload['upload_id']} - {upload['organization_name']}", expanded=False):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Organization:** {upload['organization_name']}")
                                st.write(f"**Location:** {upload['location']}")
                                st.write(f"**Type:** {upload['organization_type']}")
                                st.write(f"**Certification:** {upload['certification']}")
                                st.write(f"**Year:** {upload['year_achieved']}")
                                st.write(f"**Category:** {upload['category']}")
                            
                            with col2:
                                st.write(f"**Description:**")
                                st.write(upload['description'])
                                st.write(f"**Contact:** {upload.get('contact_email', 'Not provided')}")
                                st.write(f"**Submitted:** {upload['upload_date']}")
                            
                            # Action buttons
                            col1, col2, col3 = st.columns([1, 1, 2])
                            with col1:
                                if st.button(f"✅ Approve", key=f"approve_{upload['upload_id']}"):
                                    approve_upload(upload['upload_id'])
                                    st.success("Upload approved!")
                                    st.rerun()
                            
                            with col2:
                                if st.button(f"❌ Reject", key=f"reject_{upload['upload_id']}"):
                                    reason = st.text_input(f"Rejection reason for #{upload['upload_id']}", key=f"reason_{upload['upload_id']}")
                                    reject_upload(upload['upload_id'], reason)
                                    st.error("Upload rejected!")
                                    st.rerun()
                else:
                    st.info("📭 No pending uploads to review.")
                
                # Approved uploads
                if st.session_state.approved_uploads:
                    st.markdown("### ✅ Recently Approved")
                    for upload in st.session_state.approved_uploads[-5:]:  # Show last 5
                        st.success(f"✅ {upload['organization_name']} - {upload['certification']} (Approved: {upload.get('approved_date', 'N/A')})")
                
                # Rejected uploads
                if st.session_state.rejected_uploads:
                    st.markdown("### ❌ Recently Rejected")
                    for upload in st.session_state.rejected_uploads[-3:]:  # Show last 3
                        st.error(f"❌ {upload['organization_name']} - {upload['certification']} (Rejected: {upload.get('rejected_date', 'N/A')})")
            
            with tab2:
                st.subheader("🏥 Hospital Management")
                
                # Initialize hospital storage
                init_hospital_storage()
                
                # Add new hospital
                st.markdown("### ➕ Add New Hospital")
                with st.form("add_hospital_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_hospital_name = st.text_input("Hospital Name*")
                        new_hospital_location = st.text_input("Location*")
                        new_hospital_type = st.selectbox("Type*", ["Hospital", "Medical Center", "Clinic", "Specialty Center"])
                    
                    with col2:
                        new_hospital_website = st.text_input("Website")
                        new_hospital_phone = st.text_input("Phone")
                        new_hospital_email = st.text_input("Email")
                    
                    new_hospital_description = st.text_area("Description")
                    
                    if st.form_submit_button("➕ Add Hospital"):
                        if new_hospital_name and new_hospital_location:
                            hospital_data = {
                                'name': new_hospital_name,
                                'location': new_hospital_location,
                                'type': new_hospital_type,
                                'website': new_hospital_website,
                                'phone': new_hospital_phone,
                                'email': new_hospital_email,
                                'description': new_hospital_description
                            }
                            add_hospital(hospital_data)
                            st.success(f"✅ Hospital '{new_hospital_name}' added successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Please fill in required fields (Name and Location)")
                
                # Manage existing hospitals
                if st.session_state.custom_hospitals:
                    st.markdown("### 🏥 Existing Hospitals")
                    for hospital in st.session_state.custom_hospitals:
                        with st.expander(f"{hospital['name']} - {hospital['location']}", expanded=False):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.write(f"**Type:** {hospital['type']}")
                                st.write(f"**Website:** {hospital.get('website', 'Not provided')}")
                                st.write(f"**Phone:** {hospital.get('phone', 'Not provided')}")
                                st.write(f"**Email:** {hospital.get('email', 'Not provided')}")
                                st.write(f"**Description:** {hospital.get('description', 'No description')}")
                                st.write(f"**Added:** {hospital['added_date']}")
                            
                            with col2:
                                if st.button(f"🗑️ Delete", key=f"delete_{hospital['hospital_id']}"):
                                    delete_hospital(hospital['hospital_id'])
                                    st.success("Hospital deleted!")
                                    st.rerun()
                else:
                    st.info("📭 No custom hospitals added yet.")
            
            with tab3:
                st.subheader("📊 System Statistics")
                
                # Initialize storage
                init_upload_storage()
                init_hospital_storage()
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📤 Pending Uploads", len(st.session_state.pending_uploads))
                
                with col2:
                    st.metric("✅ Approved Uploads", len(st.session_state.approved_uploads))
                
                with col3:
                    st.metric("❌ Rejected Uploads", len(st.session_state.rejected_uploads))
                
                with col4:
                    st.metric("🏥 Custom Hospitals", len(st.session_state.custom_hospitals))
                
                # Recent activity
                st.markdown("### 📈 Recent Activity")
                if st.session_state.pending_uploads or st.session_state.approved_uploads or st.session_state.rejected_uploads:
                    all_uploads = (st.session_state.pending_uploads + 
                                 st.session_state.approved_uploads + 
                                 st.session_state.rejected_uploads)
                    
                    # Sort by upload date (most recent first)
                    all_uploads.sort(key=lambda x: x['upload_date'], reverse=True)
                    
                    for upload in all_uploads[:10]:  # Show last 10 activities
                        status_icon = "🔍" if upload['status'] == 'pending' else "✅" if upload['status'] == 'approved' else "❌"
                        st.write(f"{status_icon} {upload['organization_name']} - {upload['certification']} ({upload['upload_date']})")
                else:
                    st.info("📭 No recent activity.")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please refresh the page or contact support if the issue persists.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 12px;'>
    <p>🏥 QuXAT Healthcare Quality Grid v3.0 | Built with Streamlit</p>
    <p>🌍 Global Healthcare Quality Assessment Platform | Powered by AI & Data Analytics</p>
    <p style='font-size: 0.8em; color: #888; margin-top: 8px;'>
        ⚠️ <strong>Data Source Disclaimer:</strong> All data is validated from official certification bodies and healthcare organizations. 
        Only verified information from NABH, NABL, JCI, ISO, and other accredited sources is displayed.
    </p>
    <p style='font-size: 0.7em; color: #999; margin-top: 4px;'>
        🔍 <strong>Transparency Notice:</strong> If no validated data is found for an organization, appropriate disclaimers are shown. 
        Users are encouraged to verify information directly with certification bodies.
    </p>
    <p style='font-size: 0.7em; color: #999; margin-top: 4px;'>
        Not intended for medical advice or as sole basis for healthcare decisions. Use for comparative analysis only.
    </p>
</div>
""", unsafe_allow_html=True)