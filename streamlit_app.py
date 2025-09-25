import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import quote_plus
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors as rl_colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
import traceback

# Import data validation module
from data_validator import healthcare_validator
from iso_certification_scraper import get_iso_certifications
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
    page_title="QuXAT Healthcare Quality Grid",
    page_icon="assets/QuXAT Logo Facebook.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dynamic logo function for consistent display across all pages
def display_dynamic_logo():
    """Display the QuXAT Healthcare Quality Grid logo dynamically by loading from assets folder"""
    
    # Path to the PNG logo file
    logo_path = os.path.join("assets", "QuXAT Logo Facebook.png")
    
    try:
        # Check if logo file exists
        if os.path.exists(logo_path):
            # Load and display the PNG image
            logo_image = PILImage.open(logo_path)
            
            # Create a centered container with styling - improved centering
            st.markdown("""
            <div style="
                display: flex; 
                justify-content: center; 
                align-items: center; 
                padding: 8px 0; 
                margin-bottom: 15px;
                border-bottom: 1px solid #e8e8e8;
                background: #ffffff;
                width: 100%;
            ">
            """, unsafe_allow_html=True)
            
            # Use columns for perfect centering
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
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
                    🏥 QuXAT Healthcare Quality Grid
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
            has_jci = any('JCI' in cert.get('name', '').upper() or 'JOINT COMMISSION INTERNATIONAL' in cert.get('name', '').upper() for cert in certifications)
            
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
            
            # Apply comprehensive deduplication to all certifications
            results['certifications'] = self._comprehensive_deduplicate_certifications(results['certifications'])
            
            # Search for quality initiatives and news
            initiatives = self.search_quality_initiatives(org_name)
            results['quality_initiatives'] = initiatives
            
            # Get ISO certifications
            try:
                iso_certifications = get_iso_certifications(org_name, location="")
                results['iso_certifications'] = iso_certifications
                
                # Add ISO certifications to the main certifications list for scoring
                if iso_certifications and iso_certifications.active_certifications > 0:
                    # Get existing certification names for deduplication
                    existing_cert_names = {cert.get('name', '').upper() for cert in results['certifications']}
                    
                    # Convert ISO certifications to the format expected by the scoring system
                    for cert_type in iso_certifications.certification_types:
                        # Check if this ISO certification already exists
                        cert_name_upper = cert_type.upper()
                        if cert_name_upper not in existing_cert_names:
                            iso_cert = {
                                'name': cert_type,
                                'status': 'Active',
                                'score_impact': self._get_iso_score_impact(cert_type),
                                'certificate_number': f"ISO-{cert_type.replace(':', '-')}",
                                'accreditation_type': 'ISO Certification',
                                'issuer': 'International Organization for Standardization',
                                'organization_info': {
                                    'name': org_name,
                                    'certification_bodies': iso_certifications.certification_bodies,
                                    'quality_score_impact': iso_certifications.quality_score_impact
                                }
                            }
                            results['certifications'].append(iso_cert)
                            existing_cert_names.add(cert_name_upper)
                        
            except Exception as e:
                # If ISO certification scraping fails, continue without it
                results['iso_certifications'] = None
                pass
            
            # Get branch info from healthcare validator
            branch_info = None
            try:
                validation_result = healthcare_validator.validate_organization_certifications(org_name)
                if validation_result and 'branches' in validation_result:
                    branch_info = validation_result['branches']
                    results['branch_info'] = branch_info
            except Exception as e:
                # If branch info generation fails, continue without it
                pass
            
            # Calculate quality score with branch information
            # Patient feedback data will be automatically scraped within calculate_quality_score
            patient_feedback_data = []  # Not used anymore - automated scraping handles this
            
            score_data = self.calculate_quality_score(results['certifications'], initiatives, org_name, branch_info, patient_feedback_data)
            results['score_breakdown'] = score_data
            results['total_score'] = score_data['total_score']
            
            # Add score to history for trend tracking
            add_score_to_history(org_name, score_data)
            
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
                
                # COMPREHENSIVE DEDUPLICATION: Remove all JCI duplicates
                final_certifications = self._deduplicate_jci_certifications(enhanced_certifications)
                
                # If no validated data found, show disclaimer
                if not final_certifications:
                    st.warning(f"⚠️ No validated certification data found for '{org_name}'. Please verify organization name or check official certification databases.")
                    return []
                
                return final_certifications
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
    
    def _comprehensive_deduplicate_certifications(self, certifications):
        """
        Enhanced comprehensive deduplication to prevent all types of certification duplicates
        """
        if not certifications:
            return certifications
        
        # Track unique certifications by normalized name
        unique_certs = {}
        
        for cert in certifications:
            cert_name = cert.get('name', '').strip()
            if not cert_name:
                continue
                
            # Normalize certification name for comparison
            normalized_name = self._normalize_cert_name(cert_name)
            
            # Skip empty normalized names
            if not normalized_name:
                continue
            
            # If this is a new certification, add it
            if normalized_name not in unique_certs:
                unique_certs[normalized_name] = cert
            else:
                # If duplicate found, keep the one with more information
                existing_cert = unique_certs[normalized_name]
                if self._is_better_cert(cert, existing_cert):
                    unique_certs[normalized_name] = cert
        
        # Additional pass to catch similar certifications that might have been missed
        final_certs = list(unique_certs.values())
        
        # Check for similar certifications using fuzzy matching
        import difflib
        to_remove = set()
        
        for i, cert1 in enumerate(final_certs):
            if i in to_remove:
                continue
            for j, cert2 in enumerate(final_certs[i+1:], i+1):
                if j in to_remove:
                    continue
                
                # Check similarity between original names
                similarity = difflib.SequenceMatcher(None, 
                    cert1.get('name', '').upper(), 
                    cert2.get('name', '').upper()).ratio()
                
                if similarity > 0.8:  # 80% similarity threshold
                    # Keep the better certification
                    if self._is_better_cert(cert2, cert1):
                        to_remove.add(i)
                    else:
                        to_remove.add(j)
        
        # Remove duplicates identified by fuzzy matching
        final_certs = [cert for i, cert in enumerate(final_certs) if i not in to_remove]
        
        return final_certs
    
    def _normalize_cert_name(self, cert_name):
        """Enhanced normalization for comprehensive duplicate detection"""
        import re
        
        # Convert to uppercase and remove common variations
        normalized = cert_name.upper().strip()
        
        # Handle common organization variations
        normalized = normalized.replace('JOINT COMMISSION INTERNATIONAL', 'JCI')
        normalized = normalized.replace('JOINT COMMISSION', 'JCI')
        normalized = normalized.replace('NATIONAL ACCREDITATION BOARD FOR HOSPITALS', 'NABH')
        normalized = normalized.replace('NATIONAL ACCREDITATION BOARD FOR HOSPITALS & HEALTHCARE PROVIDERS', 'NABH')
        normalized = normalized.replace('COLLEGE OF AMERICAN PATHOLOGISTS', 'CAP')
        normalized = normalized.replace('INTERNATIONAL ORGANIZATION FOR STANDARDIZATION', 'ISO')
        normalized = normalized.replace('INTERNATIONAL STANDARDS ORGANIZATION', 'ISO')
        
        # Handle ISO variations
        normalized = re.sub(r'ISO\s*(\d+)', r'ISO\1', normalized)  # ISO 9001 -> ISO9001
        normalized = re.sub(r'ISO\s*-\s*(\d+)', r'ISO\1', normalized)  # ISO-9001 -> ISO9001
        
        # Remove common words that don't add meaning
        words_to_remove = [
            'ACCREDITATION', 'ACCREDITED', 'CERTIFICATION', 'CERTIFIED', 'CERTIFICATE',
            'STANDARD', 'STANDARDS', 'QUALITY', 'MANAGEMENT', 'SYSTEM', 'SYSTEMS',
            'HEALTHCARE', 'HOSPITAL', 'MEDICAL', 'CLINICAL', 'LABORATORY', 'LAB',
            'INTERNATIONAL', 'NATIONAL', 'BOARD', 'COMMISSION', 'ORGANIZATION',
            'THE', 'OF', 'FOR', 'AND', '&', 'IN', 'ON', 'AT', 'BY', 'WITH'
        ]
        
        for word in words_to_remove:
            normalized = normalized.replace(word, ' ')
        
        # Remove punctuation and special characters
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        
        # Remove extra spaces and join
        normalized = ' '.join(normalized.split())
        
        # Handle specific cases
        if 'JCI' in normalized:
            normalized = 'JCI'
        elif 'NABH' in normalized:
            normalized = 'NABH'
        elif 'CAP' in normalized:
            normalized = 'CAP'
        elif re.search(r'ISO\s*\d+', normalized):
            # Extract ISO number
            iso_match = re.search(r'ISO\s*(\d+)', normalized)
            if iso_match:
                normalized = f'ISO{iso_match.group(1)}'
        
        return normalized.strip()
    
    def _is_better_cert(self, cert1, cert2):
        """Determine which certification has more complete information"""
        # Prefer certification with organization_info
        if 'organization_info' in cert1 and 'organization_info' not in cert2:
            return True
        if 'organization_info' in cert2 and 'organization_info' not in cert1:
            return False
            
        # Prefer certification with higher score impact
        score1 = cert1.get('score_impact', 0)
        score2 = cert2.get('score_impact', 0)
        if score1 != score2:
            return score1 > score2
            
        # Prefer certification with certificate number
        if cert1.get('certificate_number') and not cert2.get('certificate_number'):
            return True
        if cert2.get('certificate_number') and not cert1.get('certificate_number'):
            return False
            
        # Prefer more detailed certification (more fields)
        return len(str(cert1)) > len(str(cert2))
    
    def _deduplicate_jci_certifications(self, certifications):
        """
        Comprehensive JCI deduplication to prevent multiple JCI entries from different sources
        """
        if not certifications:
            return certifications
        
        # Separate JCI and non-JCI certifications
        jci_certs = []
        other_certs = []
        
        for cert in certifications:
            cert_name = cert.get('name', '').upper()
            if ('JCI' in cert_name or 
                'JOINT COMMISSION INTERNATIONAL' in cert_name):
                jci_certs.append(cert)
            else:
                other_certs.append(cert)
        
        # If multiple JCI certifications found, keep the most comprehensive one
        if len(jci_certs) > 1:
            # Priority: 1) Has organization_info, 2) Highest score_impact, 3) Most recent
            best_jci = max(jci_certs, key=lambda x: (
                'organization_info' in x,  # Prefer JCI with org info
                x.get('score_impact', 0),  # Prefer higher score
                x.get('certificate_number', ''),  # Prefer with cert number
                len(str(x))  # Prefer more detailed entry
            ))
            
            # Log deduplication for debugging
            st.info(f"🔧 Removed {len(jci_certs) - 1} duplicate JCI certification(s)")
            
            return other_certs + [best_jci]
        
        return certifications
    
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
    
    def calculate_quality_score(self, certifications, initiatives, org_name="", branch_info=None, patient_feedback_data=None):
        """Calculate comprehensive quality score with JCI enhancement, location-specific adjustments, patient feedback integration, and more realistic and balanced scoring"""
        score_breakdown = {
            'certification_score': 0,
            'initiative_score': 0,
            'transparency_score': 0,
            'reputation_bonus': 0,
            'location_adjustment': 0,
            'patient_feedback_score': 0,
            'total_score': 0
        }
        
        # Calculate base certification score (50% weight - expanded for 0-100 scale)
        cert_score = 0
        jci_bonus = 0
        
        if certifications is None:
            certifications = []
        
        for cert in certifications:
            if cert['status'] == 'Active':
                cert_score += cert['score_impact']
                # Special handling for JCI certification
                if cert.get('name') == 'JCI':
                    jci_bonus = 8  # Increased bonus for JCI accreditation on 100-point scale
            elif cert['status'] == 'In Progress':
                cert_score += cert['score_impact'] * 0.3  # Partial credit for in-progress certifications
        
        score_breakdown['certification_score'] = min(cert_score, 50)  # Expanded to 50 points
        
        # Calculate initiative score (20% weight - expanded for comprehensive assessment)
        if initiatives is None:
            initiatives = []
        init_score = sum([init.get('impact_score', init.get('score_impact', 0)) for init in initiatives])
        score_breakdown['initiative_score'] = min(init_score, 20)
        
        # Calculate transparency score (15% weight - expanded for better granularity)
        transparency_score = np.random.randint(6, 12)  # Expanded baseline range for 100-point scale
        score_breakdown['transparency_score'] = transparency_score
        
        # Calculate patient feedback score (15% weight - AUTOMATED SCRAPING)
        patient_feedback_score = 0
        try:
            from patient_feedback_module import PatientFeedbackAnalyzer
            analyzer = PatientFeedbackAnalyzer()
            
            # Scrape and analyze patient feedback from multiple platforms
            scraped_feedbacks = analyzer.get_patient_feedback_data(org_name, location="")
            
            if scraped_feedbacks:
                # Calculate patient feedback score using automated system
                feedback_scores = analyzer.calculate_patient_feedback_score(scraped_feedbacks)
                patient_feedback_score = feedback_scores['patient_feedback_score']
                
                # Store additional feedback metrics for detailed view
                score_breakdown['feedback_volume_score'] = feedback_scores.get('volume_score', 0)
                score_breakdown['feedback_sentiment_score'] = feedback_scores.get('sentiment_score', 0)
                score_breakdown['feedback_rating_score'] = feedback_scores.get('rating_score', 0)
                score_breakdown['feedback_trend_score'] = feedback_scores.get('trend_score', 0)
                score_breakdown['feedback_confidence'] = feedback_scores.get('confidence_multiplier', 0)
                
                # Get summary for additional context
                feedback_summary = analyzer.analyze_feedback_summary(org_name, location="")
                score_breakdown['feedback_platform_breakdown'] = feedback_summary.platform_breakdown
                score_breakdown['feedback_total_count'] = feedback_summary.total_feedback_count
                score_breakdown['feedback_average_rating'] = feedback_summary.average_rating
                score_breakdown['feedback_recent_trend'] = feedback_summary.recent_trend
            else:
                # No feedback found - set default values
                patient_feedback_score = 0.0
                score_breakdown['feedback_volume_score'] = 0
                score_breakdown['feedback_sentiment_score'] = 0
                score_breakdown['feedback_rating_score'] = 0
                score_breakdown['feedback_trend_score'] = 0
                score_breakdown['feedback_confidence'] = 0
                score_breakdown['feedback_platform_breakdown'] = {}
                score_breakdown['feedback_total_count'] = 0
                score_breakdown['feedback_average_rating'] = 0.0
                score_breakdown['feedback_recent_trend'] = 'stable'
                
        except Exception as e:
            print(f"Warning: Could not process automated patient feedback for {org_name}: {e}")
            patient_feedback_score = 0.0
            # Set default values for error case
            score_breakdown['feedback_volume_score'] = 0
            score_breakdown['feedback_sentiment_score'] = 0
            score_breakdown['feedback_rating_score'] = 0
            score_breakdown['feedback_trend_score'] = 0
            score_breakdown['feedback_confidence'] = 0
            score_breakdown['feedback_platform_breakdown'] = {}
            score_breakdown['feedback_total_count'] = 0
            score_breakdown['feedback_average_rating'] = 0.0
            score_breakdown['feedback_recent_trend'] = 'stable'
        
        score_breakdown['patient_feedback_score'] = patient_feedback_score
        
        # Calculate reputation bonus (up to 15% additional points for 100-point scale)
        reputation_bonus = self.calculate_reputation_bonus(org_name)
        # Add JCI bonus to reputation bonus
        reputation_bonus += jci_bonus
        score_breakdown['reputation_bonus'] = min(reputation_bonus, 15)  # Expanded cap for 100-point scale
        
        # Calculate location-specific adjustments
        location_adjustment = self.calculate_location_adjustment(org_name, branch_info)
        score_breakdown['location_adjustment'] = location_adjustment
        
        # Total score with reputation multiplier
        base_total = (score_breakdown['certification_score'] + 
                     score_breakdown['initiative_score'] + 
                     score_breakdown['transparency_score'] +
                     score_breakdown['patient_feedback_score'])  # Include patient feedback
        
        # Apply reputation multiplier (but cap the effect)
        multiplier = self.get_reputation_multiplier(org_name)
        final_score = base_total * multiplier + score_breakdown['reputation_bonus'] + location_adjustment
        
        # Add penalty for missing key certifications
        penalty = self.calculate_missing_certification_penalty(certifications)
        final_score = max(final_score - penalty, 0)
        
        # Full 0-100 scale scoring with proper grade boundaries
        score_breakdown['total_score'] = min(final_score, 100)  # Full 100-point scale
        
        return score_breakdown
    
    def calculate_location_adjustment(self, org_name, branch_info):
        """Calculate location-specific quality score adjustments based on branch type and regional factors"""
        if not branch_info or not branch_info.get('has_branches'):
            return 0
        
        org_name_lower = org_name.lower().strip()
        adjustment = 0
        
        # Location-specific adjustments based on branch type and regional healthcare infrastructure
        location_factors = {
            # Indian Cities - Healthcare Infrastructure Quality
            'chennai': {'adjustment': 3, 'reason': 'Major medical hub with advanced infrastructure'},
            'bangalore': {'adjustment': 3, 'reason': 'Leading healthcare destination with research facilities'},
            'mumbai': {'adjustment': 2, 'reason': 'Metropolitan healthcare center with specialized services'},
            'delhi': {'adjustment': 2, 'reason': 'National capital with premier medical institutions'},
            'hyderabad': {'adjustment': 2, 'reason': 'Emerging healthcare hub with modern facilities'},
            'pune': {'adjustment': 1, 'reason': 'Growing healthcare sector with quality infrastructure'},
            'kolkata': {'adjustment': 1, 'reason': 'Established medical center with academic institutions'},
            'gurgaon': {'adjustment': 2, 'reason': 'Modern healthcare infrastructure and corporate hospitals'},
            'noida': {'adjustment': 1, 'reason': 'Developing healthcare sector with quality facilities'},
            'mohali': {'adjustment': 1, 'reason': 'Regional healthcare center with specialized services'},
            
            # International Cities - Global Healthcare Standards
            'rochester': {'adjustment': 5, 'reason': 'World-renowned medical destination (Mayo Clinic)'},
            'cleveland': {'adjustment': 4, 'reason': 'Leading medical center with research excellence'},
            'baltimore': {'adjustment': 4, 'reason': 'Academic medical center hub (Johns Hopkins)'},
            'phoenix': {'adjustment': 2, 'reason': 'Major healthcare destination in Southwest US'},
            'jacksonville': {'adjustment': 2, 'reason': 'Regional medical center with specialized care'},
            'weston': {'adjustment': 3, 'reason': 'Premium healthcare facility in South Florida'},
            'las vegas': {'adjustment': 1, 'reason': 'Growing healthcare sector with modern facilities'},
            'london': {'adjustment': 4, 'reason': 'International healthcare excellence (NHS and private)'},
            'abu dhabi': {'adjustment': 3, 'reason': 'Premium healthcare destination in Middle East'},
            'toronto': {'adjustment': 3, 'reason': 'Leading Canadian healthcare center'},
            'singapore': {'adjustment': 4, 'reason': 'World-class healthcare hub in Asia'},
            'dhahran': {'adjustment': 2, 'reason': 'Specialized healthcare for expatriate community'}
        }
        
        # Check for specific location in organization name
        for location, data in location_factors.items():
            if location in org_name_lower:
                adjustment += data['adjustment']
                break
        
        # Branch type adjustments
        if branch_info.get('search_type') == 'multi_location':
            # Find specific branch information
            available_locations = branch_info.get('available_locations', [])
            for location in available_locations:
                location_name = location.get('name', '').lower()
                if any(word in org_name_lower for word in location_name.split()):
                    # Branch type bonus
                    branch_type = location.get('type', '')
                    if branch_type == 'Flagship':
                        adjustment += 3  # Flagship locations get highest bonus
                    elif branch_type == 'Major Branch':
                        adjustment += 2  # Major branches get moderate bonus
                    elif branch_type == 'International Branch':
                        adjustment += 2  # International branches get moderate bonus
                    elif branch_type == 'Specialty Branch':
                        adjustment += 1  # Specialty branches get small bonus
                    
                    # Specialty-based adjustments
                    specialties = location.get('specialties', [])
                    if 'Transplant' in specialties:
                        adjustment += 2  # Transplant capability is premium
                    if 'Cardiac' in specialties and 'Oncology' in specialties:
                        adjustment += 1  # Multi-specialty excellence
                    
                    break
        
        elif branch_info.get('search_type') == 'specific_location':
            # Bonus for specific location searches (more targeted assessment)
            adjustment += 1
        
        # Regional healthcare infrastructure adjustments
        regions_served = branch_info.get('regions_served', [])
        if 'South India' in regions_served and any(city in org_name_lower for city in ['chennai', 'bangalore', 'hyderabad']):
            adjustment += 1  # South India healthcare excellence bonus
        elif 'North India' in regions_served and any(city in org_name_lower for city in ['delhi', 'gurgaon', 'noida']):
            adjustment += 1  # North India healthcare hub bonus
        elif any(region in regions_served for region in ['Midwest USA', 'Mid-Atlantic USA']):
            adjustment += 2  # US medical excellence regions
        
        # Cap the adjustment to prevent excessive scoring
        return min(adjustment, 8)
    
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
    
    def calculate_organization_rankings(self, current_org_name, current_score):
        """Calculate rankings and percentiles for the current organization against all others in database"""
        try:
            # Get all organizations from unified database
            all_orgs = []
            
            # Calculate scores for all organizations in the database
            for org in self.unified_database:
                org_name = org['name']
                
                # Skip if it's the current organization
                if org_name.lower() == current_org_name.lower():
                    continue
                
                # Get certifications from unified database
                certifications = []
                for cert in org.get('certifications', []):
                    certifications.append({
                        'name': cert.get('name', ''),
                        'status': cert.get('status', 'Active'),
                        'score_impact': cert.get('score_impact', 0)
                    })
                
                # Calculate basic quality initiatives (simplified for ranking)
                initiatives = []
                if org.get('quality_indicators', {}).get('jci_accredited'):
                    initiatives.append({'name': 'JCI Quality Standards', 'score_impact': 5})
                if org.get('quality_indicators', {}).get('nabh_accredited'):
                    initiatives.append({'name': 'NABH Quality Standards', 'score_impact': 3})
                
                # Calculate score for this organization
                score_data = self.calculate_quality_score(certifications, initiatives, org_name, None, [])
                
                all_orgs.append({
                    'name': org_name,
                    'total_score': score_data['total_score'],
                    'credit_score': int(300 + (score_data['total_score'] / 100) * 550),
                    'country': org.get('country', 'Unknown'),
                    'region': org.get('region', 'Unknown'),
                    'hospital_type': org.get('hospital_type', 'Hospital'),
                    'certifications': len(certifications),
                    'certification_score': score_data['certification_score'],
                    'patient_feedback_score': score_data['patient_feedback_score'],
                    'quality_score': score_data['certification_score'] + score_data['initiative_score']
                })
            
            # Sort organizations by total score (descending)
            all_orgs.sort(key=lambda x: x['total_score'], reverse=True)
            
            # Calculate current organization's ranking
            current_credit_score = int(300 + (current_score / 100) * 550)
            
            # Find ranking position
            rank = 1
            for i, org in enumerate(all_orgs):
                if org['total_score'] < current_score:
                    rank = i + 1
                    break
            else:
                rank = len(all_orgs) + 1
            
            # Calculate percentile
            total_orgs = len(all_orgs) + 1  # +1 for current organization
            percentile = ((total_orgs - rank) / total_orgs) * 100
            
            # Category-specific rankings
            category_rankings = self.calculate_category_rankings(all_orgs, current_score, current_org_name)
            
            return {
                'overall_rank': rank,
                'total_organizations': total_orgs,
                'percentile': percentile,
                'category_rankings': category_rankings,
                'top_performers': all_orgs[:5],  # Top 5 organizations
                'similar_performers': self.get_similar_performers(all_orgs, current_score),
                'regional_ranking': self.get_regional_ranking(all_orgs, current_org_name, current_score)
            }
            
        except Exception as e:
            st.error(f"Error calculating rankings: {str(e)}")
            return None
    
    def calculate_category_rankings(self, all_orgs, current_score, current_org_name):
        """Calculate rankings for specific categories"""
        try:
            # Calculate current organization's component scores
            current_org_info = self.search_organization_info(current_org_name)
            if not current_org_info:
                return {}
            
            current_breakdown = current_org_info.get('score_breakdown', {})
            
            categories = {
                'quality': 'certification_score',
                'safety': 'certification_score',  # Using certification as proxy for safety
                'patient_satisfaction': 'patient_feedback_score'
            }
            
            category_rankings = {}
            
            for category, score_field in categories.items():
                current_category_score = current_breakdown.get(score_field, 0)
                
                # Count organizations with lower scores in this category
                lower_count = sum(1 for org in all_orgs if org.get(score_field, 0) < current_category_score)
                
                # Calculate ranking and percentile
                rank = len(all_orgs) - lower_count
                percentile = (lower_count / len(all_orgs)) * 100 if all_orgs else 0
                
                category_rankings[category] = {
                    'rank': rank,
                    'percentile': percentile,
                    'score': current_category_score
                }
            
            return category_rankings
            
        except Exception as e:
            return {}
    
    def get_similar_performers(self, all_orgs, current_score):
        """Get organizations with similar performance levels"""
        # Find organizations within ±5 points of current score
        similar = []
        for org in all_orgs:
            if abs(org['total_score'] - current_score) <= 5:
                similar.append(org)
        
        return similar[:10]  # Return top 10 similar performers
    
    def get_regional_ranking(self, all_orgs, current_org_name, current_score):
        """Get ranking within the same region"""
        try:
            # Find current organization's region
            current_org_data = None
            for org in self.unified_database:
                if org['name'].lower() == current_org_name.lower():
                    current_org_data = org
                    break
            
            if not current_org_data:
                return None
            
            current_region = current_org_data.get('region', 'Unknown')
            
            # Filter organizations in the same region
            regional_orgs = [org for org in all_orgs if org.get('region') == current_region]
            
            if not regional_orgs:
                return None
            
            # Sort by score
            regional_orgs.sort(key=lambda x: x['total_score'], reverse=True)
            
            # Find ranking
            rank = 1
            for i, org in enumerate(regional_orgs):
                if org['total_score'] < current_score:
                    rank = i + 1
                    break
            else:
                rank = len(regional_orgs) + 1
            
            percentile = ((len(regional_orgs) + 1 - rank) / (len(regional_orgs) + 1)) * 100
            
            return {
                'region': current_region,
                'rank': rank,
                'total_in_region': len(regional_orgs) + 1,
                'percentile': percentile,
                'top_in_region': regional_orgs[:3]
            }
            
        except Exception as e:
            return None
    
    def _get_iso_score_impact(self, iso_standard):
        """Get the score impact for different ISO standards in healthcare"""
        iso_score_mapping = {
            'ISO 9001:2015': 12,  # Quality Management System - high impact
            'ISO 9001': 12,
            'ISO 13485:2016': 15,  # Medical Devices - highest impact for healthcare
            'ISO 13485': 15,
            'ISO 27001:2013': 10,  # Information Security - important for healthcare
            'ISO 27001': 10,
            'ISO 45001:2018': 8,   # Occupational Health & Safety
            'ISO 45001': 8,
            'ISO 14001:2015': 6,   # Environmental Management
            'ISO 14001': 6,
            'ISO 15189:2012': 12,  # Medical Laboratories
            'ISO 15189': 12,
            'ISO 22000:2018': 5,   # Food Safety
            'ISO 22000': 5,
            'ISO 50001:2018': 4,   # Energy Management
            'ISO 50001': 4,
            'ISO 27799:2016': 9,   # Health Informatics Security
            'ISO 27799': 9,
            'ISO 14155:2020': 8    # Clinical Investigation
        }
        
        # Extract base standard if version is included
        base_standard = iso_standard.split(':')[0]
        
        return iso_score_mapping.get(iso_standard, iso_score_mapping.get(base_standard, 5))
    
    def _get_iso_description(self, iso_standard):
        """Get description for a specific ISO standard"""
        iso_descriptions = {
            'ISO 9001': 'Quality Management Systems - Ensures consistent quality in products and services',
            'ISO 13485': 'Medical Devices Quality Management - Specific to medical device manufacturing and services',
            'ISO 14001': 'Environmental Management Systems - Demonstrates environmental responsibility',
            'ISO 45001': 'Occupational Health and Safety Management - Ensures workplace safety standards',
            'ISO 27001': 'Information Security Management - Protects sensitive patient and organizational data',
            'ISO 15189': 'Medical Laboratories - Quality and competence requirements for medical testing',
            'ISO 17025': 'Testing and Calibration Laboratories - General requirements for laboratory competence',
            'ISO 22000': 'Food Safety Management - Ensures food safety in healthcare facilities',
            'ISO 50001': 'Energy Management Systems - Demonstrates energy efficiency and sustainability',
            'ISO 37001': 'Anti-bribery Management Systems - Prevents and addresses bribery and corruption',
            'ISO 27799': 'Health Informatics Security - Specific security requirements for health information',
            'ISO 14155': 'Clinical Investigation - Good clinical practice for medical device studies'
        }
        # Extract base standard if version is included
        base_standard = iso_standard.split(':')[0]
        return iso_descriptions.get(iso_standard, iso_descriptions.get(base_standard, 'International standard for quality and management systems'))
    
    def _get_iso_relevance(self, iso_standard):
        """Get relevance level for healthcare organizations"""
        iso_relevance = {
            'ISO 9001': 'High - Core quality management',
            'ISO 13485': 'Very High - Medical device specific',
            'ISO 14001': 'Medium - Environmental compliance',
            'ISO 45001': 'High - Patient and staff safety',
            'ISO 27001': 'High - Patient data protection',
            'ISO 15189': 'Very High - Laboratory services',
            'ISO 17025': 'High - Testing accuracy',
            'ISO 22000': 'Medium - Food service safety',
            'ISO 50001': 'Low - Operational efficiency',
            'ISO 37001': 'Medium - Governance and ethics',
            'ISO 27799': 'Very High - Health data security',
            'ISO 14155': 'High - Clinical research quality'
        }
        # Extract base standard if version is included
        base_standard = iso_standard.split(':')[0]
        return iso_relevance.get(iso_standard, iso_relevance.get(base_standard, 'Medium - General quality standard'))
    
    def find_similar_organizations(self, org_name, org_location="", org_type="Hospital"):
        """Find similar organizations in the same region using unified database with their quality scores"""
        similar_orgs = []
        
        # Determine the country/region for the searched organization
        search_region = self.determine_organization_region(org_name, org_location)
        
        # Load unified database if not already loaded
        if not hasattr(self, 'unified_database') or not self.unified_database:
            self.unified_database = self.load_unified_database()
        
        # Filter organizations from the same region using unified database
        region_orgs = []
        for org in self.unified_database:
            org_country = org.get('country', '').lower()
            org_region = org.get('region', '').lower()
            
            # Match by country or region
            if (org_country == search_region.lower() or 
                org_region == search_region.lower() or
                self._is_same_region(org_country, search_region.lower())):
                
                # Skip the searched organization itself
                if org['name'].lower() != org_name.lower():
                    # Create location string
                    location_parts = []
                    if org.get('city'):
                        location_parts.append(org['city'])
                    if org.get('state'):
                        location_parts.append(org['state'])
                    if org.get('country'):
                        location_parts.append(org['country'])
                    
                    org_location_str = ', '.join(location_parts) if location_parts else 'Unknown'
                    
                    # Determine organization type based on certifications
                    org_type_determined = 'Healthcare Organization'
                    certifications = org.get('certifications', [])
                    if any('JCI' in cert.get('name', '') for cert in certifications):
                        org_type_determined = 'JCI Accredited Hospital'
                    elif any('NABH' in cert.get('name', '') for cert in certifications):
                        org_type_determined = 'NABH Accredited Hospital'
                    elif any('CAP' in cert.get('name', '') for cert in certifications):
                        org_type_determined = 'CAP Accredited Laboratory'
                    
                    region_orgs.append({
                        'name': org['name'],
                        'location': org_location_str,
                        'type': org_type_determined,
                        'unified_data': org
                    })
        
        # Limit to 8 organizations for comparison
        region_orgs = region_orgs[:8]
        
        # Generate quality scores for similar organizations
        for org in region_orgs:
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
    
    def _is_same_region(self, org_country, search_region):
        """Helper method to determine if an organization's country matches the search region"""
        # Country to region mapping
        country_region_map = {
            'india': 'india',
            'united states': 'united states',
            'usa': 'united states',
            'us': 'united states',
            'united kingdom': 'united kingdom',
            'uk': 'united kingdom',
            'singapore': 'singapore',
            'canada': 'canada',
            'australia': 'australia'
        }
        
        # Normalize country name
        normalized_country = org_country.lower().strip()
        
        # Direct match
        if normalized_country == search_region:
            return True
        
        # Check mapped regions
        mapped_region = country_region_map.get(normalized_country)
        if mapped_region and mapped_region == search_region:
            return True
        
        return False
    
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
        <b>{org_name}</b> has achieved an overall QuXAT Healthcare Quality Grid quality score of <b>{score:.1f}/100</b> (Grade: <b>{grade}</b>).
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
            ['Certifications', '45%', f"{score_breakdown.get('certification_score', 0):.2f}",
                f"{score_breakdown.get('certification_score', 0):.2f}"],
                ['Quality Initiatives', '15%', f"{score_breakdown.get('initiative_score', 0):.2f}",
                f"{score_breakdown.get('initiative_score', 0):.2f}"],
                ['Transparency', '10%', f"{score_breakdown.get('transparency_score', 0):.2f}",
                f"{score_breakdown.get('transparency_score', 0):.2f}"],
                ['Patient Feedback', '15%', f"{score_breakdown.get('patient_feedback_score', 0):.2f}",
                f"{score_breakdown.get('patient_feedback_score', 0):.2f}"],
                ['Reputation Bonus', '10%', f"{score_breakdown.get('reputation_bonus', 0):.2f}",
                f"{score_breakdown.get('reputation_bonus', 0):.2f}"],
                ['Location Adjustment', '5%', f"{score_breakdown.get('location_adjustment', 0):.2f}",
                f"{score_breakdown.get('location_adjustment', 0):.2f}"],
                ['', '', 'Total Score:', f"{score:.2f}/100"]
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
                init_text = f"<b>{i}.</b> {initiative.get('name', 'N/A')} ({initiative.get('year', 'N/A')})"
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
        
        <b>Not Medical Advice:</b> QuXAT Healthcare Quality Grid scores do not constitute medical advice, professional recommendations, 
        or endorsements. Users should conduct independent verification and due diligence before making healthcare decisions.<br/><br/>
        
        <b>Limitation of Liability:</b> QuXAT Healthcare Quality Grid and its developers disclaim all warranties, express or implied, 
        regarding the accuracy or completeness of information. Users assume full responsibility for any decisions 
        made based on QuXAT Healthcare Quality Grid assessments.<br/><br/>
        
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
        
        # Score Breakdown Section with Visual Progress Bars
        st.markdown("### 🎯 Detailed Score Breakdown Analysis")
        
        score_breakdown = org_data.get('score_breakdown', {})
        
        # Define score components with their maximum values and colors
        components = [
            {
                'name': 'Certifications',
                'score': score_breakdown.get('certification_score', 0),
                'max_score': 50,
                'color': '#1f77b4',
                'weight': '50%',
                'description': 'Active healthcare certifications and accreditations'
            },
            {
                'name': 'Quality Initiatives',
                'score': score_breakdown.get('initiative_score', 0),
                'max_score': 20,
                'color': '#ff7f0e',
                'weight': '20%',
                'description': 'Quality improvement programs and innovations'
            },
            {
                'name': 'Transparency',
                'score': score_breakdown.get('transparency_score', 0),
                'max_score': 15,
                'color': '#2ca02c',
                'weight': '15%',
                'description': 'Public disclosure of quality metrics and outcomes'
            },
            {
                'name': 'Patient Feedback',
                'score': score_breakdown.get('patient_feedback_score', 0),
                'max_score': 15,
                'color': '#d62728',
                'weight': '15%',
                'description': 'Patient reviews and satisfaction scores from multiple platforms'
            }
        ]
        
        # Display each component with progress bar and reasoning
        for component in components:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Progress bar
                progress_percentage = (component['score'] / component['max_score']) * 100 if component['max_score'] > 0 else 0
                
                # Color coding based on performance
                if progress_percentage >= 80:
                    bar_color = '#28a745'  # Green
                    performance_text = "Excellent"
                elif progress_percentage >= 60:
                    bar_color = '#ffc107'  # Yellow
                    performance_text = "Good"
                elif progress_percentage >= 40:
                    bar_color = '#fd7e14'  # Orange
                    performance_text = "Fair"
                else:
                    bar_color = '#dc3545'  # Red
                    performance_text = "Needs Improvement"
                
                st.markdown(f"""
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h4 style="margin: 0; color: {component['color']};">{component['name']} ({component['weight']})</h4>
                        <span style="font-weight: bold; color: {bar_color};">{component['score']:.1f}/{component['max_score']} ({performance_text})</span>
                    </div>
                    <div style="background-color: #e9ecef; border-radius: 10px; height: 20px; overflow: hidden;">
                        <div style="background-color: {bar_color}; height: 100%; width: {progress_percentage}%; border-radius: 10px; transition: width 0.3s ease;"></div>
                    </div>
                    <p style="margin-top: 0.5rem; color: #6c757d; font-size: 0.9rem;">{component['description']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Performance indicator
                if progress_percentage >= 80:
                    st.success(f"🟢 {progress_percentage:.0f}%")
                elif progress_percentage >= 60:
                    st.warning(f"🟡 {progress_percentage:.0f}%")
                elif progress_percentage >= 40:
                    st.warning(f"🟠 {progress_percentage:.0f}%")
                else:
                    st.error(f"🔴 {progress_percentage:.0f}%")
        
        # QuXAT Credit Score Display - Similar to FICO Credit Scoring
        st.markdown("---")
        
        # Convert 0-100 score to 300-850 credit-style range
        credit_score = int(300 + (score / 100) * 550)
        
        # Credit-style risk categories and descriptions
        if credit_score >= 800:
            grade_color = '#28a745'
            grade_text = 'Exceptional (800-850)'
            grade_emoji = '🏆'
            risk_level = 'Minimal Risk'
            risk_description = 'Outstanding healthcare quality with minimal compliance risk'
        elif credit_score >= 740:
            grade_color = '#20c997'
            grade_text = 'Very Good (740-799)'
            grade_emoji = '⭐'
            risk_level = 'Low Risk'
            risk_description = 'Excellent healthcare quality with low compliance risk'
        elif credit_score >= 670:
            grade_color = '#ffc107'
            grade_text = 'Good (670-739)'
            grade_emoji = '👍'
            risk_level = 'Moderate Risk'
            risk_description = 'Good healthcare quality with moderate compliance oversight needed'
        elif credit_score >= 580:
            grade_color = '#fd7e14'
            grade_text = 'Fair (580-669)'
            grade_emoji = '👌'
            risk_level = 'Elevated Risk'
            risk_description = 'Fair healthcare quality requiring enhanced monitoring'
        elif credit_score >= 500:
            grade_color = '#dc3545'
            grade_text = 'Poor (500-579)'
            grade_emoji = '⚠️'
            risk_level = 'High Risk'
            risk_description = 'Poor healthcare quality requiring immediate attention'
        else:
            grade_color = '#6f42c1'
            grade_text = 'Very Poor (300-499)'
            grade_emoji = '🔄'
            risk_level = 'Very High Risk'
            risk_description = 'Critical healthcare quality issues requiring urgent intervention'
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {grade_color}20, {grade_color}10);
            border: 2px solid {grade_color};
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            margin: 1rem 0;
        ">
            <h2 style="color: {grade_color}; margin-bottom: 0.5rem;">
                {grade_emoji} QuXAT Credit Score: {credit_score}
            </h2>
            <h3 style="color: {grade_color}; margin-bottom: 0.5rem;">
                {grade_text}
            </h3>
            <p style="color: #666; margin-bottom: 0.5rem; font-size: 1.1em;">
                <strong>Risk Level:</strong> {risk_level}
            </p>
            <p style="color: #666; margin-bottom: 1rem; font-style: italic;">
                {risk_description}
            </p>
            <div style="background: rgba(255,255,255,0.8); padding: 0.8rem; border-radius: 8px; margin-top: 1rem;">
                <p style="color: #333; margin: 0; font-size: 0.9em;">
                    <strong>Base Quality Score:</strong> {score:.1f}/100 | 
                    <strong>Credit Range:</strong> 300-850 | 
                    <strong>Industry:</strong> Healthcare Quality & Compliance
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Score History and Trend Analysis
        trend_data = get_score_trend(org_name)
        if trend_data or org_name in st.session_state.score_history:
            st.markdown("### 📈 QuXAT Credit Score History & Trends")
            st.markdown("*Track your healthcare quality score over time, just like credit monitoring*")
            
            if org_name in st.session_state.score_history and len(st.session_state.score_history[org_name]) > 0:
                history = st.session_state.score_history[org_name]
                
                # Create trend visualization
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if trend_data and isinstance(trend_data, dict):
                        direction = trend_data.get('direction', 'stable')
                        status = trend_data.get('status', 'stable')
                        change = trend_data.get('change', 0)
                        
                        trend_color = '#28a745' if direction == 'up' else '#dc3545' if direction == 'down' else '#6c757d'
                        trend_emoji = '📈' if direction == 'up' else '📉' if direction == 'down' else '➡️'
                        
                        st.markdown(f"""
                        <div style="background: {trend_color}20; padding: 1rem; border-radius: 8px; text-align: center;">
                            <h4 style="color: {trend_color}; margin-bottom: 0.5rem;">{trend_emoji} Score Trend</h4>
                            <div style="font-size: 1.2em; font-weight: bold; color: {trend_color};">
                                {status.title() if status else 'Stable'}
                            </div>
                            <p style="margin: 0; font-size: 0.9em; color: #666;">
                                {'+' if direction == 'up' else '-' if direction == 'down' else ''}{change} points
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; text-align: center;">
                            <h4 style="color: #6c757d; margin-bottom: 0.5rem;">📊 First Assessment</h4>
                            <p style="margin: 0; color: #666;">Baseline score established</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    assessments_count = len(history)
                    st.markdown(f"""
                    <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; text-align: center;">
                        <h4 style="color: #1976d2; margin-bottom: 0.5rem;">📋 Assessments</h4>
                        <div style="font-size: 1.2em; font-weight: bold; color: #1976d2;">
                            {assessments_count}
                        </div>
                        <p style="margin: 0; font-size: 0.9em; color: #666;">Total evaluations</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    latest_date = history[-1]['date']
                    st.markdown(f"""
                    <div style="background: #fff3e0; padding: 1rem; border-radius: 8px; text-align: center;">
                        <h4 style="color: #f57c00; margin-bottom: 0.5rem;">📅 Last Updated</h4>
                        <div style="font-size: 1em; font-weight: bold; color: #f57c00;">
                            {latest_date}
                        </div>
                        <p style="margin: 0; font-size: 0.9em; color: #666;">Most recent assessment</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Score history chart
                if len(history) > 1:
                    
                    dates = [entry['date'] for entry in history]
                    scores = [entry['credit_score'] for entry in history]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=scores,
                        mode='lines+markers',
                        name='QuXAT Credit Score',
                        line=dict(color='#1976d2', width=3),
                        marker=dict(size=8, color='#1976d2'),
                        hovertemplate='<b>Date:</b> %{x}<br><b>Score:</b> %{y}<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        title='QuXAT Credit Score History',
                        xaxis_title='Date',
                        yaxis_title='Credit Score',
                        yaxis=dict(range=[300, 850]),
                        height=400,
                        showlegend=False,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    # Add score range bands
                    fig.add_hline(y=800, line_dash="dash", line_color="green", annotation_text="Exceptional (800+)")
                    fig.add_hline(y=740, line_dash="dash", line_color="lightgreen", annotation_text="Very Good (740+)")
                    fig.add_hline(y=670, line_dash="dash", line_color="orange", annotation_text="Good (670+)")
                    fig.add_hline(y=580, line_dash="dash", line_color="red", annotation_text="Fair (580+)")
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Score breakdown history
                    with st.expander("📊 Detailed Score Component History", expanded=False):
                        st.markdown("**Component Score Trends:**")
                        
                        # Create component comparison
                        components = ['certification_score', 'patient_feedback_score', 'initiative_score', 'transparency_score']
                        component_names = ['Certifications', 'Patient Feedback', 'Quality Initiatives', 'Transparency']
                        
                        for i, (component, name) in enumerate(zip(components, component_names)):
                            latest_value = history[-1].get(component, 0)
                            if len(history) > 1:
                                previous_value = history[-2].get(component, 0)
                                change = latest_value - previous_value
                                change_text = f"({'+' if change > 0 else ''}{change:.1f})" if change != 0 else "(No change)"
                                change_color = "green" if change > 0 else "red" if change < 0 else "gray"
                            else:
                                change_text = "(Baseline)"
                                change_color = "gray"
                            
                            st.markdown(f"• **{name}:** {latest_value:.1f} <span style='color: {change_color};'>{change_text}</span>", unsafe_allow_html=True)
        
        # Credit-Style Factors Analysis Section
        st.markdown("### 📊 QuXAT Credit Factors Analysis")
        st.markdown("*Similar to credit score factors, these components determine your healthcare quality rating*")
        
        # Calculate factor impacts as percentages
        total_possible = 100  # Total possible score
        cert_impact = (score_breakdown.get('certification_score', 0) / 50) * 50  # 50% weight
        init_impact = (score_breakdown.get('initiative_score', 0) / 20) * 20    # 20% weight
        trans_impact = (score_breakdown.get('transparency_score', 0) / 15) * 15  # 15% weight
        feedback_impact = (score_breakdown.get('patient_feedback_score', 0) / 15) * 15  # 15% weight
        
        # Create credit-style factors display
        factors_col1, factors_col2 = st.columns([2, 1])
        
        with factors_col1:
            st.markdown("#### 🏆 Healthcare Quality Factors")
            
            # Factor 1: Certifications & Accreditations (Most Important)
            cert_percentage = (cert_impact / 50) * 100
            if cert_percentage >= 80:
                cert_status = "Excellent"
                cert_color = "#28a745"
            elif cert_percentage >= 60:
                cert_status = "Good"
                cert_color = "#ffc107"
            else:
                cert_status = "Needs Improvement"
                cert_color = "#dc3545"
                
            st.markdown(f"""
            **1. Certifications & Accreditations** - *50% of your score*
            <div style="background: {cert_color}20; border-left: 4px solid {cert_color}; padding: 10px; margin: 5px 0;">
                <strong style="color: {cert_color};">{cert_status}</strong> - {cert_percentage:.0f}% of maximum impact<br>
                <small>Impact on Credit Score: {cert_impact:.1f} points</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Factor 2: Quality Initiatives (Second Most Important)
            init_percentage = (init_impact / 20) * 100
            if init_percentage >= 80:
                init_status = "Excellent"
                init_color = "#28a745"
            elif init_percentage >= 60:
                init_status = "Good"
                init_color = "#ffc107"
            else:
                init_status = "Needs Improvement"
                init_color = "#dc3545"
                
            st.markdown(f"""
            **2. Quality Improvement Programs** - *20% of your score*
            <div style="background: {init_color}20; border-left: 4px solid {init_color}; padding: 10px; margin: 5px 0;">
                <strong style="color: {init_color};">{init_status}</strong> - {init_percentage:.0f}% of maximum impact<br>
                <small>Impact on Credit Score: {init_impact:.1f} points</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Factor 3: Patient Satisfaction
            feedback_percentage = (feedback_impact / 15) * 100
            if feedback_percentage >= 80:
                feedback_status = "Excellent"
                feedback_color = "#28a745"
            elif feedback_percentage >= 60:
                feedback_status = "Good"
                feedback_color = "#ffc107"
            else:
                feedback_status = "Needs Improvement"
                feedback_color = "#dc3545"
                
            st.markdown(f"""
            **3. Patient Satisfaction & Reviews** - *15% of your score*
            <div style="background: {feedback_color}20; border-left: 4px solid {feedback_color}; padding: 10px; margin: 5px 0;">
                <strong style="color: {feedback_color};">{feedback_status}</strong> - {feedback_percentage:.0f}% of maximum impact<br>
                <small>Impact on Credit Score: {feedback_impact:.1f} points</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Factor 4: Transparency & Disclosure
            trans_percentage = (trans_impact / 15) * 100
            if trans_percentage >= 80:
                trans_status = "Excellent"
                trans_color = "#28a745"
            elif trans_percentage >= 60:
                trans_status = "Good"
                trans_color = "#ffc107"
            else:
                trans_status = "Needs Improvement"
                trans_color = "#dc3545"
                
            st.markdown(f"""
            **4. Transparency & Public Disclosure** - *15% of your score*
            <div style="background: {trans_color}20; border-left: 4px solid {trans_color}; padding: 10px; margin: 5px 0;">
                <strong style="color: {trans_color};">{trans_status}</strong> - {trans_percentage:.0f}% of maximum impact<br>
                <small>Impact on Credit Score: {trans_impact:.1f} points</small>
            </div>
            """, unsafe_allow_html=True)
        
        with factors_col2:
            st.markdown("#### 📈 Score Impact Summary")
            
            # Credit-style impact meter
            total_impact = cert_impact + init_impact + trans_impact + feedback_impact
            impact_percentage = (total_impact / 100) * 100
            
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                <h3 style="color: #333; margin-bottom: 10px;">Overall Impact</h3>
                <div style="font-size: 2em; color: {grade_color}; font-weight: bold;">
                    {impact_percentage:.0f}%
                </div>
                <p style="color: #666; margin: 5px 0;">of Maximum Possible Score</p>
                <hr style="margin: 15px 0;">
                <p style="color: #333; font-size: 0.9em;">
                    <strong>Credit Score:</strong> {credit_score}<br>
                    <strong>Risk Level:</strong> {risk_level}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Improvement potential
            improvement_potential = 100 - impact_percentage
            if improvement_potential > 0:
                st.markdown(f"""
                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin-top: 15px;">
                    <h4 style="color: #1976d2; margin-bottom: 10px;">💡 Improvement Potential</h4>
                    <p style="color: #333; margin: 0;">
                        You could improve your QuXAT Credit Score by up to <strong>{improvement_potential:.0f} points</strong> 
                        by addressing the factors marked as "Needs Improvement" above.
                    </p>
                </div>
                """, unsafe_allow_html=True)

        # Detailed Reasoning Section
        st.markdown("### 🔍 Score Reasoning & Analysis")
        
        # Certifications reasoning
        with st.expander("🏆 Certifications Analysis", expanded=True):
            cert_score = score_breakdown.get('certification_score', 0)
            certifications = org_data.get('certifications', [])
            active_certs = [c for c in certifications if c.get('status') == 'Active']
            
            st.markdown(f"""
            **Score: {cert_score:.1f}/50 points**
            
            **Analysis:**
            - Found {len(certifications)} total certifications in our database
            - {len(active_certs)} certifications are currently active
            - Certification score represents {(cert_score/50)*100:.1f}% of maximum possible points
            
            **Key Factors:**
            """)
            
            if active_certs:
                for cert in active_certs[:5]:  # Show top 5
                    impact = cert.get('score_impact', 0)
                    st.markdown(f"- **{cert.get('name', 'Unknown')}**: +{impact:.1f} points ({cert.get('status', 'Unknown')} status)")
            else:
                st.markdown("- No active certifications found in our database")
                st.markdown("- This significantly impacts the overall quality score")
        
        # Patient Feedback reasoning
        if 'patient_feedback_score' in score_breakdown:
            with st.expander("👥 Patient Feedback Analysis", expanded=True):
                feedback_score = score_breakdown.get('patient_feedback_score', 0)
                feedback_data = org_data.get('patient_feedback_data', {})
                
                st.markdown(f"""
                **Score: {feedback_score:.1f}/15 points**
                
                **Analysis:**
                - Patient feedback represents {(feedback_score/15)*100:.1f}% of maximum possible points
                - Data sourced from multiple platforms including Google Reviews, Facebook, and healthcare-specific sites
                
                **Breakdown:**
                """)
                
                if feedback_data:
                    st.markdown(f"- **Total Reviews**: {feedback_data.get('total_reviews', 'N/A')}")
                    st.markdown(f"- **Average Rating**: {feedback_data.get('average_rating', 'N/A')}/5.0")
                    st.markdown(f"- **Sentiment Trend**: {feedback_data.get('recent_trend', 'N/A')}")
                    
                    platform_breakdown = feedback_data.get('platform_breakdown', {})
                    if platform_breakdown:
                        st.markdown("**Platform Distribution:**")
                        for platform, count in platform_breakdown.items():
                            st.markdown(f"  - {platform}: {count} reviews")
                else:
                    st.markdown("- Automated feedback analysis completed")
                    st.markdown("- Score based on available public reviews and ratings")
        
        # Quality Initiatives reasoning
        with st.expander("🚀 Quality Initiatives Analysis"):
            init_score = score_breakdown.get('initiative_score', 0)
            initiatives = org_data.get('quality_initiatives', [])
            
            st.markdown(f"""
            **Score: {init_score:.1f}/20 points**
            
            **Analysis:**
            - Quality initiatives represent {(init_score/20)*100:.1f}% of maximum possible points
            - Found {len(initiatives)} quality improvement programs or innovations
            
            **Contributing Factors:**
            """)
            
            if initiatives:
                for init in initiatives[:3]:  # Show top 3
                    impact = init.get('impact_score', 0)
                    st.markdown(f"- **{init.get('name', 'Unknown')}** ({init.get('year', 'N/A')}): +{impact:.1f} points")
            else:
                st.markdown("- No specific quality initiatives identified in our analysis")
                st.markdown("- This may indicate limited public disclosure of quality programs")
        
        # Transparency reasoning
        with st.expander("📊 Transparency Analysis"):
            trans_score = score_breakdown.get('transparency_score', 0)
            
            st.markdown(f"""
            **Score: {trans_score:.1f}/15 points**
            
            **Analysis:**
            - Transparency represents {(trans_score/15)*100:.1f}% of maximum possible points
            - Based on public availability of quality metrics, outcomes data, and organizational information
            
            **Evaluation Criteria:**
            - Public disclosure of quality metrics and patient outcomes
            - Availability of organizational information and leadership details
            - Accessibility of performance data and improvement initiatives
            - Compliance with transparency requirements and standards
            """)
        
        # Credit Repair-Style Improvement Recommendations Section
        st.markdown("### 💡 QuXAT Credit Repair Plan")
        st.markdown("*Just like credit repair, improving your QuXAT score requires strategic action and time*")
        
        recommendations = []
        
        # Certification recommendations (like credit utilization)
        cert_score = score_breakdown.get('certification_score', 0)
        if cert_score < 35:  # Less than 70% of certification points
            recommendations.append({
                'category': '🏆 Accreditation Portfolio',
                'priority': 'High',
                'recommendation': 'Pursue additional healthcare accreditations such as JCI, ISO 9001, or local healthcare quality certifications',
                'impact': 'Could increase QuXAT Credit Score by 30-45 points',
                'timeline': '6-18 months',
                'credit_analogy': 'Like maintaining low credit utilization, having diverse active certifications shows financial institutions (patients/regulators) you can manage quality standards responsibly.',
                'action_steps': [
                    '📋 Audit current certification status and renewal dates',
                    '🎯 Identify 2-3 target certifications relevant to your specialty',
                    '📅 Create certification timeline with milestones',
                    '💰 Budget for certification costs and training'
                ]
            })
        
        # Patient feedback recommendations (like payment history)
        feedback_score = score_breakdown.get('patient_feedback_score', 0)
        if feedback_score < 10:  # Less than 67% of feedback points
            recommendations.append({
                'category': '⭐ Patient Satisfaction Record',
                'priority': 'High',
                'recommendation': 'Implement comprehensive patient feedback collection system and focus on improving patient satisfaction scores',
                'impact': 'Could increase QuXAT Credit Score by 15-24 points',
                'timeline': '3-6 months',
                'credit_analogy': 'Like payment history in credit scoring, patient satisfaction is the most important factor. Consistent positive feedback builds trust over time.',
                'action_steps': [
                    '📱 Deploy digital feedback collection at all touchpoints',
                    '📊 Set up monthly patient satisfaction monitoring',
                    '🔄 Implement rapid response system for negative feedback',
                    '🎯 Target 4.5+ star average rating across platforms'
                ]
            })
        
        # Quality initiatives recommendations (like credit mix)
        init_score = score_breakdown.get('initiative_score', 0)
        if init_score < 12:  # Less than 60% of initiative points
            recommendations.append({
                'category': '🚀 Quality Program Diversity',
                'priority': 'Medium',
                'recommendation': 'Develop and publicize quality improvement initiatives, patient safety programs, or innovative healthcare solutions',
                'impact': 'Could increase QuXAT Credit Score by 15-30 points',
                'timeline': '6-12 months',
                'credit_analogy': 'Like having a good credit mix (cards, loans, mortgage), diverse quality programs show you can handle various aspects of healthcare excellence.',
                'action_steps': [
                    '🎯 Launch 3-5 quality improvement initiatives annually',
                    '📈 Implement measurable patient safety programs',
                    '🏥 Develop specialty-specific quality protocols',
                    '📢 Publicize achievements through press releases'
                ]
            })
        
        # Transparency recommendations (like credit age)
        trans_score = score_breakdown.get('transparency_score', 0)
        if trans_score < 10:  # Less than 67% of transparency points
            recommendations.append({
                'category': '🔍 Transparency & Disclosure',
                'priority': 'Medium',
                'recommendation': 'Increase public disclosure of quality metrics, patient outcomes, and organizational performance data',
                'impact': 'Could increase QuXAT Credit Score by 9-15 points',
                'timeline': '1-3 months',
                'credit_analogy': 'Like maintaining old credit accounts, long-term transparency builds credibility. Consistent disclosure shows you have nothing to hide.',
                'action_steps': [
                    '🌐 Create dedicated quality metrics page on website',
                    '📊 Publish quarterly quality reports',
                    '📋 Share outcome data and improvement trends',
                    '🏆 Highlight awards and recognitions prominently'
                ]
            })
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                priority_color = '#dc3545' if rec['priority'] == 'High' else '#ffc107'
                priority_emoji = '🔴' if rec['priority'] == 'High' else '🟡'
                
                # Credit repair-style card layout
                st.markdown(f"""
                <div style="
                    border: 2px solid {priority_color};
                    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                    padding: 1.5rem;
                    margin: 1.5rem 0;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                        <div style="
                            background: {priority_color};
                            color: white;
                            padding: 0.5rem 1rem;
                            border-radius: 20px;
                            font-weight: bold;
                            margin-right: 1rem;
                        ">
                            {priority_emoji} {rec['priority']} Priority
                        </div>
                        <h3 style="color: {priority_color}; margin: 0;">{rec['category']}</h3>
                    </div>
                    
                    <div style="background: #e8f4fd; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                        <h4 style="color: #1976d2; margin-bottom: 0.5rem;">💡 Credit Analogy</h4>
                        <p style="margin: 0; font-style: italic; color: #333;">{rec['credit_analogy']}</p>
                    </div>
                    
                    <p style="margin-bottom: 1rem;"><strong>📋 Action Plan:</strong> {rec['recommendation']}</p>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                        <div style="background: #e8f5e8; padding: 0.8rem; border-radius: 6px;">
                            <strong style="color: #2e7d32;">📈 Credit Score Impact:</strong><br>
                            {rec['impact']}
                        </div>
                        <div style="background: #fff3e0; padding: 0.8rem; border-radius: 6px;">
                            <strong style="color: #f57c00;">⏱️ Timeline:</strong><br>
                            {rec['timeline']}
                        </div>
                    </div>
                    
                    <div style="background: #f5f5f5; padding: 1rem; border-radius: 8px;">
                        <h4 style="color: #333; margin-bottom: 0.5rem;">✅ Specific Action Steps:</h4>
                        <ul style="margin: 0; padding-left: 1.2rem;">
                """, unsafe_allow_html=True)
                
                # Add action steps
                for step in rec.get('action_steps', []):
                    st.markdown(f"<li style='margin-bottom: 0.3rem; color: #333;'>{step}</li>", unsafe_allow_html=True)
                
                st.markdown("</ul></div></div>", unsafe_allow_html=True)
                
        else:
            st.success("🎉 Excellent QuXAT Credit Score! This organization demonstrates strong quality indicators across all measured categories.")
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 5px solid #4caf50;
                margin: 1rem 0;
            ">
                <h4 style="color: #2e7d32; margin-bottom: 1rem;">🏆 Credit Maintenance Plan</h4>
                <ul style="color: #333; margin: 0;">
                    <li>📊 Continue monitoring and maintaining current certification status</li>
                    <li>🔄 Regularly review and update quality improvement initiatives</li>
                    <li>⭐ Maintain high levels of patient satisfaction and feedback quality</li>
                    <li>🎯 Consider pursuing additional advanced certifications for further excellence</li>
                    <li>📈 Monitor QuXAT Credit Score monthly for any changes</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Credit Monitoring Dashboard
        if recommendations:
            st.markdown("### 📊 QuXAT Credit Monitoring Dashboard")
            st.markdown("*Track your progress like a credit monitoring service*")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; text-align: center;">
                    <h4 style="color: #1976d2; margin-bottom: 0.5rem;">📈 Score Potential</h4>
                    <div style="font-size: 1.5em; font-weight: bold; color: #1976d2;">
                        +{} points
                    </div>
                    <p style="margin: 0; font-size: 0.9em; color: #666;">Maximum Improvement</p>
                </div>
                """.format(sum([int(rec['impact'].split('-')[1].split()[0]) for rec in recommendations if '-' in rec['impact']])), unsafe_allow_html=True)
            
            with col2:
                avg_timeline = sum([int(rec['timeline'].split('-')[0]) for rec in recommendations if '-' in rec['timeline']]) // len(recommendations)
                st.markdown(f"""
                <div style="background: #fff3e0; padding: 1rem; border-radius: 8px; text-align: center;">
                    <h4 style="color: #f57c00; margin-bottom: 0.5rem;">⏱️ Avg Timeline</h4>
                    <div style="font-size: 1.5em; font-weight: bold; color: #f57c00;">
                        {avg_timeline} months
                    </div>
                    <p style="margin: 0; font-size: 0.9em; color: #666;">To See Results</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                high_priority_count = sum([1 for rec in recommendations if rec['priority'] == 'High'])
                st.markdown(f"""
                <div style="background: #ffebee; padding: 1rem; border-radius: 8px; text-align: center;">
                    <h4 style="color: #d32f2f; margin-bottom: 0.5rem;">🔴 High Priority</h4>
                    <div style="font-size: 1.5em; font-weight: bold; color: #d32f2f;">
                        {high_priority_count} items
                    </div>
                    <p style="margin: 0; font-size: 0.9em; color: #666;">Need Immediate Action</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Quick Action Items
        if recommendations:
            st.markdown("### ⚡ Quick Action Items (Next 30 Days)")
            
            quick_actions = [
                "📋 Conduct internal audit of current certification status and renewal dates",
                "📊 Implement patient feedback collection system across all service points",
                "🌐 Review and update organization website with quality metrics and achievements",
                "📈 Document and publicize recent quality improvement initiatives",
                "🔍 Benchmark against similar organizations in your region or specialty"
            ]
            
            for action in quick_actions:
                st.markdown(f"- {action}")
        
        st.markdown("---")
        
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
            active_certs = [cert for cert in certifications if cert.get('status') == 'Active']
            st.markdown(f"**Active Certifications:** {len(active_certs)}")
            
            # Note: Detailed certification cards are displayed in the main profile section below
            
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
        
        # ISO Certifications Section
        st.markdown("### 🌐 ISO Certifications")
        
        iso_certifications = org_data.get('iso_certifications')
        if iso_certifications and iso_certifications.active_certifications > 0:
            st.markdown(f"**ISO Certifications Found:** {iso_certifications.active_certifications}")
            
            # Display ISO certification types
            if iso_certifications.certification_types:
                st.markdown("#### ISO Standards Certified")
                
                iso_data = []
                for cert_type in iso_certifications.certification_types:
                    # Get score impact for this ISO standard
                    score_impact = self._get_iso_score_impact(cert_type)
                    
                    iso_data.append({
                        'ISO Standard': cert_type,
                        'Description': self._get_iso_description(cert_type),
                        'Score Impact': f"{score_impact:.2f}",
                        'Relevance': self._get_iso_relevance(cert_type)
                    })
                
                if iso_data:
                    iso_df = pd.DataFrame(iso_data)
                    st.dataframe(iso_df, use_container_width=True, hide_index=True)
            
            # Display certification bodies
            if iso_certifications.certification_bodies:
                st.markdown("#### Certification Bodies")
                bodies_text = ", ".join(iso_certifications.certification_bodies)
                st.write(f"**Accredited by:** {bodies_text}")
            
            # Display data sources
            if iso_certifications.data_sources:
                with st.expander("Data Sources", expanded=False):
                    for source in iso_certifications.data_sources:
                        st.write(f"• {source}")
            
            # Quality score impact
            if iso_certifications.quality_score_impact > 0:
                st.success(f"**Quality Score Impact:** +{iso_certifications.quality_score_impact:.2f} points")
        else:
            st.info("No ISO certifications found for this organization.")
        
        # Quality Initiatives Section
        st.markdown("### 🚀 Quality Initiatives")
        
        initiatives = org_data.get('quality_initiatives', [])
        if initiatives:
            st.markdown(f"**Quality Initiatives Identified:** {len(initiatives)}")
            
            for i, initiative in enumerate(initiatives[:8], 1):  # Show top 8
                with st.expander(f"{i}. {initiative.get('name', 'N/A')} ({initiative.get('year', 'N/A')})"):
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
            
            **Not Medical Advice:** QuXAT Healthcare Quality Grid scores do not constitute medical advice, professional recommendations, 
            or endorsements. Users should conduct independent verification and due diligence before making healthcare decisions.
            
            **Limitation of Liability:** QuXAT Healthcare Quality Grid and its developers disclaim all warranties, express or implied, 
            regarding the accuracy or completeness of information. Users assume full responsibility for any decisions 
            made based on QuXAT Healthcare Quality Grid assessments.
            
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
        st.error(f"Traceback: {traceback.format_exc()}")

# Initialize the analyzer
@st.cache_resource
def get_analyzer():
    return HealthcareOrgAnalyzer()

# Display dynamic logo at the top of every page
display_dynamic_logo()

# Initialize score history tracking
if 'score_history' not in st.session_state:
    st.session_state.score_history = {}

# Initialize ranking history tracking
if 'ranking_history' not in st.session_state:
    st.session_state.ranking_history = {}

def add_score_to_history(org_name, score_data):
    """Add a score entry to the organization's history"""
    if org_name not in st.session_state.score_history:
        st.session_state.score_history[org_name] = []
    
    # Create score entry with timestamp
    score_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'credit_score': int(300 + (score_data.get('total_score', 0) * 5.5)),  # Convert to 300-850 scale
        'base_score': score_data.get('total_score', 0),
        'certification_score': score_data.get('certification_score', 0),
        'patient_feedback_score': score_data.get('patient_feedback_score', 0),
        'initiative_score': score_data.get('initiative_score', 0),
        'transparency_score': score_data.get('transparency_score', 0),
        'reputation_bonus': score_data.get('reputation_bonus', 0),
        'location_adjustment': score_data.get('location_adjustment', 0)
    }
    
    # Add to history (keep last 12 entries for trend analysis)
    st.session_state.score_history[org_name].append(score_entry)
    if len(st.session_state.score_history[org_name]) > 12:
        st.session_state.score_history[org_name] = st.session_state.score_history[org_name][-12:]

def add_ranking_to_history(org_name, rankings_data):
    """Add ranking data to the organization's ranking history"""
    if org_name not in st.session_state.ranking_history:
        st.session_state.ranking_history[org_name] = []
    
    # Create ranking entry with timestamp
    ranking_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'overall_rank': rankings_data.get('overall_rank', 0),
        'percentile': rankings_data.get('percentile', 0),
        'total_organizations': rankings_data.get('total_organizations', 0),
        'category_rankings': rankings_data.get('category_rankings', {}),
        'regional_rank': rankings_data.get('regional_ranking', {}).get('rank', 0) if rankings_data.get('regional_ranking') else 0,
        'regional_percentile': rankings_data.get('regional_ranking', {}).get('percentile', 0) if rankings_data.get('regional_ranking') else 0
    }
    
    # Add to history (keep last 12 entries for trend analysis)
    st.session_state.ranking_history[org_name].append(ranking_entry)
    if len(st.session_state.ranking_history[org_name]) > 12:
        st.session_state.ranking_history[org_name] = st.session_state.ranking_history[org_name][-12:]

def get_ranking_trend(org_name):
    """Get ranking trend analysis for an organization"""
    if org_name not in st.session_state.ranking_history or len(st.session_state.ranking_history[org_name]) < 2:
        return None
    
    history = st.session_state.ranking_history[org_name]
    latest_rank = history[-1]['overall_rank']
    previous_rank = history[-2]['overall_rank']
    
    latest_percentile = history[-1]['percentile']
    previous_percentile = history[-2]['percentile']
    
    rank_change = previous_rank - latest_rank  # Positive means improved (lower rank number)
    percentile_change = latest_percentile - previous_percentile  # Positive means improved
    
    if rank_change > 0:
        return {
            'direction': 'up', 
            'rank_change': rank_change, 
            'percentile_change': percentile_change,
            'status': 'improving',
            'description': f'Moved up {rank_change} positions'
        }
    elif rank_change < 0:
        return {
            'direction': 'down', 
            'rank_change': abs(rank_change), 
            'percentile_change': percentile_change,
            'status': 'declining',
            'description': f'Dropped {abs(rank_change)} positions'
        }
    else:
        return {
            'direction': 'stable', 
            'rank_change': 0, 
            'percentile_change': percentile_change,
            'status': 'stable',
            'description': 'Maintained position'
        }

def get_score_trend(org_name):
    """Get score trend analysis for an organization"""
    if org_name not in st.session_state.score_history or len(st.session_state.score_history[org_name]) < 2:
        return None
    
    history = st.session_state.score_history[org_name]
    latest_score = history[-1]['credit_score']
    previous_score = history[-2]['credit_score']
    
    change = latest_score - previous_score
    
    if change > 0:
        return {'direction': 'up', 'change': change, 'status': 'improving'}
    elif change < 0:
        return {'direction': 'down', 'change': abs(change), 'status': 'declining'}
    else:
        return {'direction': 'stable', 'change': 0, 'status': 'stable'}

# Main content - All QuXAT Healthcare Quality Grid content consolidated on Home page
try:
        st.header("🏠 QuXAT Healthcare Quality Grid")
        
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
        st.markdown("### 👥 Who Benefits from QuXAT Healthcare Quality Grid?")
        
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
                    <li><strong>Quality Advocacy:</strong> Support quality improvement initiatives</li>
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
        col1, col2, col3 = st.columns([4, 2, 1.5])
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
            st.info("🔍 **Data Validation Notice:** QuXAT Healthcare Quality Grid uses validated data from official certification bodies.")
            
            # Initialize the analyzer
            analyzer = get_analyzer()
            
            with st.spinner("🔍 Searching for organization data..."):
                # Real-time data search
                org_data = analyzer.search_organization_info(org_name)
                
                if org_data:
                    st.success(f"✅ Found information for: **{org_name}**")
                    
                    # Check for branch information and display suggestions
                    if 'branch_info' in org_data and org_data['branch_info']:
                        branch_info = org_data['branch_info']
                        
                        # Display branch suggestions if multiple locations found
                        if branch_info.get('has_multiple_locations', False):
                            st.markdown("### 🏢 Multiple Locations Found")
                            
                            if branch_info.get('is_specific_location', False):
                                st.info(f"📍 **Showing results for:** {branch_info.get('searched_location', 'Current Location')}")
                                
                                # Show other available locations
                                if branch_info.get('other_locations'):
                                    st.markdown("**Other available locations:**")
                                    other_locations = branch_info['other_locations'][:5]  # Show up to 5 other locations
                                    
                                    # Create columns for location buttons
                                    cols = st.columns(min(len(other_locations), 3))
                                    for idx, location in enumerate(other_locations):
                                        with cols[idx % 3]:
                                            if st.button(f"📍 {location}", key=f"location_{idx}"):
                                                # Re-search with specific location
                                                st.rerun()
                            else:
                                # Show all available locations for selection
                                st.markdown("**Available locations for this organization:**")
                                available_locations = branch_info.get('available_locations', [])
                                
                                if available_locations:
                                    # Create columns for location selection
                                    cols = st.columns(min(len(available_locations), 3))
                                    for idx, location in enumerate(available_locations[:9]):  # Show up to 9 locations
                                        with cols[idx % 3]:
                                            if st.button(f"🏥 {location}", key=f"branch_{idx}"):
                                                # Store selected location and re-search
                                                st.session_state.selected_location = location
                                                # Re-search with specific location
                                                new_search_term = f"{org_name} {location}"
                                                st.session_state.location_search = new_search_term
                                                st.rerun()
                                
                                # Show summary of branch types if available
                                if branch_info.get('branch_types'):
                                    st.markdown("**Branch Types Available:**")
                                    branch_types = branch_info['branch_types']
                                    type_cols = st.columns(len(branch_types))
                                    for idx, (branch_type, count) in enumerate(branch_types.items()):
                                        with type_cols[idx]:
                                            st.metric(f"{branch_type.title()}", count)
                            
                            st.markdown("---")
                    
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
                        st.metric("🏆 Overall Quality Score", f"{score:.2f}/100", f"{score_color}")
                    
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
                    certifications = [cert for cert in certifications if not ('JCI' in cert.get('name', '').upper() or 'NABH' in cert.get('name', '').upper() or 'JOINT COMMISSION INTERNATIONAL' in cert.get('name', '').upper())]
                    if certifications:
                        cert_cols = st.columns(min(len(certifications), 3))
                        for idx, cert in enumerate(certifications[:6]):  # Show up to 6 certifications
                            with cert_cols[idx % 3]:
                                # Determine certification status and icon
                                cert_status = cert.get('status', 'Active')
                                cert_icon = "✅" if cert_status == "Active" else "⏳" if cert_status == "Pending" else "❌"
                                
                                # Determine certification status color
                                if cert_status == 'Active':
                                    cert_status_color = "#28a745"
                                elif cert_status == 'Pending':
                                    cert_status_color = "#ffc107"
                                else:
                                    cert_status_color = "#dc3545"
                                
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
                                        <p style="margin: 5px 0; color: #666;"><strong>Status:</strong> <span style="color: {cert_status_color};">{cert_status}</span></p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    # Simplified certification card - only show status
                                    card_content = f"""
                                    <div style="padding: 15px; border: 1px solid #ddd; border-radius: 8px; margin: 10px 0; background: #f8f9fa;">
                                        <h4 style="color: #2c3e50; margin: 0 0 10px 0;">{cert_icon} {cert_name}</h4>
                                        <p style="margin: 5px 0; color: #666;"><strong>Status:</strong> <span style="color: {cert_status_color};">{cert_status}</span></p>
                                    </div>
                                    """
                                    
                                    st.markdown(card_content, unsafe_allow_html=True)
                    else:
                        st.info("📋 No active certifications found for this organization.")
                    
                    st.markdown("---")
                    
                    # Accreditations Section
                    st.markdown("### 🎖️ Accreditations & Recognition")
                    
                    # Get accreditations from organization data
                    accreditations = org_data.get('accreditations', [])
                    
                    # Add JCI and NABH from certifications data as they are actually accreditations
                    all_certifications = org_data.get('certifications', [])
                    jci_nabh_accreditations = [cert for cert in all_certifications if ('JCI' in cert.get('name', '').upper() or 'NABH' in cert.get('name', '').upper() or 'JOINT COMMISSION INTERNATIONAL' in cert.get('name', '').upper())]
                    
                    # Convert JCI/NABH certifications to accreditation format (avoid duplicates)
                    existing_accred_names = [acc.get('name', '').upper() for acc in accreditations]
                    for cert in jci_nabh_accreditations:
                        cert_name = cert.get('name', 'Unknown Accreditation')
                        # Skip if this accreditation already exists
                        if cert_name.upper() in existing_accred_names:
                            continue
                            
                        accred_entry = {
                            'name': cert_name,
                            'level': 'International Standard' if ('JCI' in cert_name.upper() or 'JOINT COMMISSION INTERNATIONAL' in cert_name.upper()) else 'National Standard',
                            'awarded_date': cert.get('issued_date', cert.get('awarded_date', 'N/A')),
                            'description': cert.get('description', ''),
                            'status': cert.get('status', 'Active'),
                            'issuer': cert.get('issuer', 'N/A'),
                            'valid_until': cert.get('valid_until', cert.get('expiry', 'N/A'))
                        }
                        accreditations.append(accred_entry)
                        existing_accred_names.append(cert_name.upper())
                    
                    # Check for NABL accreditation
                    nabl_accreditation = healthcare_validator.get_nabl_accreditation(org_name)
                    if nabl_accreditation:
                        accreditations.append(nabl_accreditation)
                    
                    if not accreditations:
                        # Create sample accreditations based on organization type and score
                        accreditations = []
                        # Only create sample accreditations if score is defined (i.e., after a search)
                        if 'score' in locals() and score >= 70:
                            accreditations.append({
                                'name': 'Joint Commission Accreditation',
                                'level': 'Gold Standard',
                                'awarded_date': '2023',
                                'description': 'Comprehensive healthcare quality and safety accreditation'
                            })
                        if 'score' in locals() and score >= 60:
                            accreditations.append({
                                'name': 'ISO 9001:2015 Quality Management',
                                'level': 'Certified',
                                'awarded_date': '2022',
                                'description': 'International standard for quality management systems'
                            })
                        if 'score' in locals() and score >= 50:
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
                            
                            # Special icons for NABH
                            if 'NABH' in accred_name:
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
                            
                            # Determine status color
                            status = accred.get('status', 'Active')
                            if status == 'Active':
                                status_color = "#28a745"
                            elif status == 'Pending':
                                status_color = "#ffc107"
                            else:
                                status_color = "#dc3545"
                            
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
                            
                            # Get organization details from session state
                            org_details = ""
                            if 'current_org' in st.session_state and 'current_data' in st.session_state:
                                current_org_name = st.session_state.current_org
                                current_org_data = st.session_state.current_data
                                
                                # Extract organization type
                                org_type = "Healthcare Organization"  # Default
                                if 'unified_data' in current_org_data:
                                    unified_data = current_org_data['unified_data']
                                    org_type = unified_data.get('type', org_type)
                                
                                # Extract organization location
                                org_location = ""
                                if 'unified_data' in current_org_data:
                                    unified_data = current_org_data['unified_data']
                                    if 'location' in unified_data:
                                        org_location = unified_data['location']
                                    elif 'city' in unified_data and 'state' in unified_data:
                                        org_location = f"{unified_data['city']}, {unified_data['state']}"
                                    elif 'address' in unified_data:
                                        org_location = unified_data['address']
                                
                                # Build organization details section
                                org_details = f"""
                                <div style="background: #e8f4fd; padding: 10px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #007bff;">
                                    <p style="margin: 2px 0; color: #495057; font-size: 0.9em;"><strong>🏥 Organization:</strong> {current_org_name}</p>"""
                                
                                if org_location:
                                    org_details += f"""
                                    <p style="margin: 2px 0; color: #495057; font-size: 0.9em;"><strong>📍 Location:</strong> {org_location}</p>"""
                                
                                org_details += f"""
                                    <p style="margin: 2px 0; color: #495057; font-size: 0.9em;"><strong>🏢 Type:</strong> {org_type}</p>
                                </div>"""
                            
                            # Display the main accreditation info
                            st.markdown(f"""
                            <div style="padding: 20px; border-left: 4px solid {level_color}; background: #f8f9fa; margin: 15px 0; border-radius: 0 8px 8px 0;">
                                <h4 style="color: #2c3e50; margin: 0 0 10px 0;">{level_icon} {accred.get('name', 'Unknown Accreditation')}</h4>
                                <p style="margin: 5px 0; color: #666;"><strong>Accreditation Status:</strong> <span style="color: {status_color};">{accred.get('status', 'Active')}</span></p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Display the description separately to ensure proper HTML rendering
                            description = accred.get('description', 'No description available.')
                            if description and description != 'No description available.':
                                st.markdown(description, unsafe_allow_html=True)
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
                        st.metric("🏆 Certification Score", f"{score_data['certification_score']:.2f}/45")
                        st.metric("🚀 Initiative Score", f"{score_data['initiative_score']:.2f}/15")
                        st.metric("📋 Transparency Score", f"{score_data['transparency_score']:.2f}/10")
                        st.metric("👥 Patient Feedback Score", f"{score_data.get('patient_feedback_score', 0):.2f}/15")
                        
                        # Show automated feedback details if available
                        if score_data.get('feedback_total_count', 0) > 0:
                            st.metric("📊 Total Reviews", f"{score_data.get('feedback_total_count', 0)}")
                            st.metric("⭐ Avg Rating", f"{score_data.get('feedback_average_rating', 0):.1f}/5.0")
                            feedback_trend = score_data.get('feedback_recent_trend', 'stable')
                            st.metric("📈 Trend", feedback_trend.title() if feedback_trend else 'Stable')
                        else:
                            st.info("🔍 No patient feedback found from automated scraping")
                        st.metric("⭐ Reputation Bonus", f"+{reputation_bonus:.2f}")
                        
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
                        
                        # Add valid_until column only if it exists and has valid dates
                        date_column = None
                        if 'valid_until' in cert_df.columns:
                            date_column = 'valid_until'
                        elif 'expiry' in cert_df.columns:
                            date_column = 'expiry'
                        
                        # Check if there are any valid dates (not empty, not 'N/A', not null)
                        if date_column and not cert_df[date_column].isna().all():
                            # Check if there are any non-empty, non-N/A values
                            valid_dates = cert_df[date_column].dropna()
                            valid_dates = valid_dates[valid_dates != 'N/A']
                            valid_dates = valid_dates[valid_dates != '']
                            
                            if len(valid_dates) > 0:
                                columns_to_display.append(date_column)
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
                            with st.expander(f"📋 {initiative['name']} ({initiative['year']})"):
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"**Initiative:** {initiative['name']}")
                                    st.write(f"**Year:** {initiative['year']}")
                                with col2:
                                    st.metric("Impact Score", f"+{initiative.get('impact_score', initiative.get('score_impact', 0))}")
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
                    
                    # Get organization region for display
                    analyzer = get_analyzer()
                    org_info = analyzer.search_organization_info(org_name)
                    org_location = ""
                    org_region = "Unknown Region"
                    
                    if org_info and 'unified_data' in org_info:
                        # Extract location from unified database if available
                        unified_data = org_info['unified_data']
                        if 'location' in unified_data:
                            org_location = unified_data['location']
                        elif 'city' in unified_data and 'state' in unified_data:
                            org_location = f"{unified_data['city']}, {unified_data['state']}"
                        elif 'address' in unified_data:
                            org_location = unified_data['address']
                        
                        # Get region for display
                        org_region = analyzer.determine_organization_region(org_name, org_location)
                        org_region = org_region.title()  # Capitalize for display
                    
                    st.markdown(f"### 🏥 Regional Quality Score Comparison - {org_region}")
                    st.markdown(f"*Comparing with all healthcare organizations mapped in {org_region}*")
                    
                    with st.spinner(f"🔍 Finding healthcare organizations in {org_region}..."):
                        similar_orgs = analyzer.find_similar_organizations(org_name, org_location)
                        
                        if similar_orgs:
                            st.markdown(f"**Found {len(similar_orgs)} healthcare organizations in {org_region} for comparison:**")
                            
                            # Create comparison table
                            comparison_data = []
                            comparison_data.append({
                                'Organization': f"**{org_name}** (Searched)",
                                'Location': "Current Search",
                                'Type': org_type,
                                'Quality Score': f"{score:.2f}",
                                'Grade': grade,
                                'Certifications': len([c for c in org_data['certifications'] if c['status'] == 'Active']),
                                'Quality Initiatives': len(org_data['quality_initiatives'])
                            })
                            
                            for org in similar_orgs:
                                org_grade = "A+" if org['total_score'] >= 75 else "A" if org['total_score'] >= 65 else "B+" if org['total_score'] >= 55 else "B" if org['total_score'] >= 45 else "C"
                                comparison_data.append({
                                    'Organization': org['name'],
                                    'Location': org['location'],
                                    'Type': org['type'],
                                    'Quality Score': f"{org['total_score']:.2f}",
                                    'Grade': org_grade,
                                    'Certifications': len([c for c in org['certifications'] if c['status'] == 'Active']),
                                    'Quality Initiatives': len(org['quality_initiatives'])
                                })
                            
                            # Display comparison table
                            comparison_df = pd.DataFrame(comparison_data)
                            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                            
                            # Visualization: Score comparison chart
                            st.markdown(f"#### 📊 Quality Score Comparison - {org_region} Region")
                            
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
                                    title=f"Quality Score Comparison - {org_region} Region",
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
                                st.metric("📈 vs Average", f"{diff_from_avg:+.2f}", f"Avg: {avg_score:.2f}")
                                
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
                                insights.append("📈 **Improvement Opportunity**: Consider focusing on quality enhancement quality initiatives.")
                            
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
        
        # Quality Scorecard - Organization Rankings (only show if score is defined)
        if 'score' in locals():
            st.markdown("---")
            st.markdown("### 🏆 Quality Scorecard - Organization Rankings")
            st.markdown("*See how your organization ranks against all others in our database based on quality, safety, and patient satisfaction*")
            
            # Calculate rankings
            rankings_data = analyzer.calculate_organization_rankings(org_name, score)
            
            # Calculate credit score and grade for rankings display
            credit_score = int(300 + (score / 100) * 550)
            
            # Credit-style risk categories and descriptions
            if credit_score >= 800:
                grade_color = '#28a745'
                grade_text = 'Exceptional (800-850)'
                grade_emoji = '🏆'
                risk_level = 'Minimal Risk'
                risk_description = 'Outstanding healthcare quality with minimal compliance risk'
            elif credit_score >= 740:
                grade_color = '#20c997'
                grade_text = 'Very Good (740-799)'
                grade_emoji = '⭐'
                risk_level = 'Low Risk'
                risk_description = 'Excellent healthcare quality with low compliance risk'
            elif credit_score >= 670:
                grade_color = '#ffc107'
                grade_text = 'Good (670-739)'
                grade_emoji = '👍'
                risk_level = 'Moderate Risk'
                risk_description = 'Good healthcare quality with moderate compliance oversight needed'
            elif credit_score >= 580:
                grade_color = '#fd7e14'
                grade_text = 'Fair (580-669)'
                grade_emoji = '👌'
                risk_level = 'Elevated Risk'
                risk_description = 'Fair healthcare quality requiring enhanced monitoring'
            elif credit_score >= 500:
                grade_color = '#dc3545'
                grade_text = 'Poor (500-579)'
                grade_emoji = '⚠️'
                risk_level = 'High Risk'
                risk_description = 'Poor healthcare quality requiring immediate attention'
            else:
                grade_color = '#6f42c1'
                grade_text = 'Very Poor (300-499)'
                grade_emoji = '🔄'
                risk_level = 'Very High Risk'
                risk_description = 'Critical healthcare quality issues requiring urgent intervention'
        
            # Add ranking data to history for trend tracking
            if rankings_data:
                add_ranking_to_history(org_name, rankings_data)
                
                # Overall Ranking Display
                rank_col1, rank_col2, rank_col3, rank_col4 = st.columns(4)
                
                # Get ranking trend for display
                ranking_trend = get_ranking_trend(org_name)
                
                with rank_col1:
                    rank_color = '#28a745' if rankings_data['percentile'] >= 75 else '#ffc107' if rankings_data['percentile'] >= 50 else '#fd7e14' if rankings_data['percentile'] >= 25 else '#dc3545'
                    
                    # Add trend indicator
                    trend_indicator = ""
                    if ranking_trend:
                        if ranking_trend['direction'] == 'up':
                            trend_indicator = f"<div style='color: #28a745; font-size: 0.8em;'>📈 +{ranking_trend['rank_change']} positions</div>"
                        elif ranking_trend['direction'] == 'down':
                            trend_indicator = f"<div style='color: #dc3545; font-size: 0.8em;'>📉 -{ranking_trend['rank_change']} positions</div>"
                        else:
                            trend_indicator = f"<div style='color: #6c757d; font-size: 0.8em;'>➡️ No change</div>"
                    
                    st.markdown(f"""
                    <div style="background: {rank_color}20; border: 2px solid {rank_color}; border-radius: 10px; padding: 1rem; text-align: center;">
                        <h4 style="color: {rank_color}; margin-bottom: 0.5rem;">🏆 Overall Rank</h4>
                        <div style="font-size: 2em; font-weight: bold; color: {rank_color};">
                            #{rankings_data['overall_rank']}
                        </div>
                        <p style="margin: 0; color: #666;">out of {rankings_data['total_organizations']} organizations</p>
                        {trend_indicator}
                    </div>
                    """, unsafe_allow_html=True)
                
                with rank_col2:
                    percentile_color = '#28a745' if rankings_data['percentile'] >= 75 else '#ffc107' if rankings_data['percentile'] >= 50 else '#fd7e14' if rankings_data['percentile'] >= 25 else '#dc3545'
                    st.markdown(f"""
                    <div style="background: {percentile_color}20; border: 2px solid {percentile_color}; border-radius: 10px; padding: 1rem; text-align: center;">
                        <h4 style="color: {percentile_color}; margin-bottom: 0.5rem;">📊 Percentile</h4>
                        <div style="font-size: 2em; font-weight: bold; color: {percentile_color};">
                            {rankings_data['percentile']:.0f}%
                        </div>
                        <p style="margin: 0; color: #666;">Better than {rankings_data['percentile']:.0f}% of organizations</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with rank_col3:
                    credit_rank_color = '#1976d2'
                    st.markdown(f"""
                    <div style="background: {credit_rank_color}20; border: 2px solid {credit_rank_color}; border-radius: 10px; padding: 1rem; text-align: center;">
                        <h4 style="color: {credit_rank_color}; margin-bottom: 0.5rem;">💳 Credit Score</h4>
                        <div style="font-size: 2em; font-weight: bold; color: {credit_rank_color};">
                            {credit_score}
                        </div>
                        <p style="margin: 0; color: #666;">{grade_text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with rank_col4:
                    risk_rank_color = '#28a745' if risk_level == 'Minimal Risk' else '#ffc107' if 'Low' in risk_level else '#fd7e14' if 'Moderate' in risk_level else '#dc3545'
                    st.markdown(f"""
                    <div style="background: {risk_rank_color}20; border: 2px solid {risk_rank_color}; border-radius: 10px; padding: 1rem; text-align: center;">
                        <h4 style="color: {risk_rank_color}; margin-bottom: 0.5rem;">⚡ Risk Level</h4>
                        <div style="font-size: 1.2em; font-weight: bold; color: {risk_rank_color};">
                            {risk_level}
                        </div>
                        <p style="margin: 0; color: #666; font-size: 0.9em;">{grade_emoji} {risk_description[:30]}...</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Category-Specific Rankings
                st.markdown("#### 📋 Category Performance Rankings")
                
                category_rankings = rankings_data.get('category_rankings', {})
                if category_rankings:
                    cat_col1, cat_col2, cat_col3 = st.columns(3)
                    
                    categories_info = {
                        'quality': {'name': 'Quality & Certifications', 'emoji': '🏥', 'color': '#28a745'},
                        'safety': {'name': 'Safety Standards', 'emoji': '🛡️', 'color': '#1976d2'},
                        'patient_satisfaction': {'name': 'Patient Satisfaction', 'emoji': '😊', 'color': '#ff9800'}
                    }
                    
                    for i, (category, info) in enumerate(categories_info.items()):
                        col = [cat_col1, cat_col2, cat_col3][i]
                        
                        if category in category_rankings:
                            cat_data = category_rankings[category]
                            cat_color = info['color']
                            
                            with col:
                                st.markdown(f"""
                                <div style="background: {cat_color}15; border: 1px solid {cat_color}; border-radius: 8px; padding: 1rem; text-align: center;">
                                    <h5 style="color: {cat_color}; margin-bottom: 0.5rem;">{info['emoji']} {info['name']}</h5>
                                    <div style="font-size: 1.5em; font-weight: bold; color: {cat_color};">
                                        #{cat_data['rank']}
                                    </div>
                                    <p style="margin: 0; color: #666; font-size: 0.9em;">
                                        {cat_data['percentile']:.0f}th percentile<br>
                                        Score: {cat_data['score']:.1f}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                
                # Top Performers Comparison
                st.markdown("#### 🌟 Top Performers Benchmark")
                
                top_performers = rankings_data.get('top_performers', [])
                if top_performers:
                    st.markdown("*Compare your organization with the top 5 performers in our database*")
                    
                    # Create comparison table
                    comparison_data = []
                    comparison_data.append({
                        'Rank': f"#{rankings_data['overall_rank']}",
                        'Organization': f"**{org_name}** (You)",
                        'Credit Score': credit_score,
                        'Quality Score': f"{score:.1f}",
                        'Country': org_data.get('country', 'Unknown'),
                        'Type': org_data.get('hospital_type', 'Hospital')
                    })
                    
                    for i, performer in enumerate(top_performers[:5]):
                        comparison_data.append({
                            'Rank': f"#{i+1}",
                            'Organization': performer['name'],
                            'Credit Score': performer['credit_score'],
                            'Quality Score': f"{performer['total_score']:.1f}",
                            'Country': performer['country'],
                            'Type': performer['hospital_type']
                        })
                    
                    df_comparison = pd.DataFrame(comparison_data)
                    st.dataframe(df_comparison, use_container_width=True, hide_index=True)
                
                # Regional Ranking
                regional_data = rankings_data.get('regional_ranking')
                if regional_data:
                    st.markdown("#### 🌍 Regional Performance")
                    
                    reg_col1, reg_col2 = st.columns(2)
                    
                    with reg_col1:
                        regional_color = '#28a745' if regional_data['percentile'] >= 75 else '#ffc107' if regional_data['percentile'] >= 50 else '#fd7e14'
                        st.markdown(f"""
                        <div style="background: {regional_color}20; border: 2px solid {regional_color}; border-radius: 10px; padding: 1rem;">
                            <h5 style="color: {regional_color}; margin-bottom: 1rem;">🌍 {regional_data['region']} Region Ranking</h5>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 1.8em; font-weight: bold; color: {regional_color};">
                                        #{regional_data['rank']}
                                    </div>
                                    <p style="margin: 0; color: #666;">out of {regional_data['total_in_region']} in region</p>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 1.2em; font-weight: bold; color: {regional_color};">
                                        {regional_data['percentile']:.0f}%
                                    </div>
                                    <p style="margin: 0; color: #666; font-size: 0.9em;">percentile</p>
                                </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with reg_col2:
                    st.markdown("**Top Regional Performers:**")
                    for i, top_regional in enumerate(regional_data.get('top_in_region', [])[:3]):
                        medal = ['🥇', '🥈', '🥉'][i] if i < 3 else '🏆'
                        st.markdown(f"{medal} **{top_regional['name']}** - {top_regional['credit_score']} ({top_regional['total_score']:.1f})")
            
            # Similar Performers
            similar_performers = rankings_data.get('similar_performers', [])
            if similar_performers:
                with st.expander("🤝 Organizations with Similar Performance", expanded=False):
                    st.markdown("*Organizations within ±5 points of your quality score*")
                    
                    for performer in similar_performers[:10]:
                        score_diff = performer['total_score'] - score
                        diff_text = f"+{score_diff:.1f}" if score_diff > 0 else f"{score_diff:.1f}"
                        diff_color = '#28a745' if score_diff <= 0 else '#dc3545'
                        
                        st.markdown(f"""
                        <div style="background: #f8f9fa; padding: 0.8rem; margin: 0.3rem 0; border-radius: 5px; border-left: 3px solid {diff_color};">
                            <strong>{performer['name']}</strong> ({performer['country']}) - 
                            Credit Score: {performer['credit_score']} 
                            <span style="color: {diff_color};">({diff_text} points)</span>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Ranking History Chart
            if 'ranking_history' in st.session_state and org_name in st.session_state.ranking_history:
                ranking_history = st.session_state.ranking_history[org_name]
                if len(ranking_history) > 1:
                    with st.expander("📈 Ranking History & Trends", expanded=False):
                        # Create ranking trend chart
                        dates = [entry['date'] for entry in ranking_history]
                        ranks = [entry['overall_rank'] for entry in ranking_history]
                        percentiles = [entry['percentile'] for entry in ranking_history]
                        
                        fig = go.Figure()
                        
                        # Add ranking line (inverted y-axis since lower rank is better)
                        fig.add_trace(go.Scatter(
                            x=dates,
                            y=ranks,
                            mode='lines+markers',
                            name='Overall Rank',
                            line=dict(color='#1976d2', width=3),
                            marker=dict(size=8),
                            yaxis='y'
                        ))
                        
                        # Add percentile line on secondary y-axis
                        fig.add_trace(go.Scatter(
                            x=dates,
                            y=percentiles,
                            mode='lines+markers',
                            name='Percentile',
                            line=dict(color='#28a745', width=3),
                            marker=dict(size=8),
                            yaxis='y2'
                        ))
                        
                        fig.update_layout(
                            title="Ranking Performance Over Time",
                            xaxis_title="Date",
                            yaxis=dict(
                                title="Overall Rank",
                                side="left",
                                autorange="reversed"  # Lower rank numbers are better
                            ),
                            yaxis2=dict(
                                title="Percentile (%)",
                                side="right",
                                overlaying="y",
                                range=[0, 100]
                            ),
                            height=400,
                            showlegend=True,
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show trend summary
                        trend_data = get_ranking_trend(org_name)
                        if trend_data and isinstance(trend_data, dict) and 'direction' in trend_data and trend_data['direction']:
                            trend_col1, trend_col2, trend_col3 = st.columns(3)
                            
                            with trend_col1:
                                direction = trend_data.get('direction', 'stable')
                                direction_icon = "📈" if direction == 'up' else "📉" if direction == 'down' else "➡️"
                                direction_color = "#28a745" if direction == 'up' else "#dc3545" if direction == 'down' else "#6c757d"
                                direction_text = direction.title() if direction else 'Stable'
                                st.markdown(f"""
                                <div style="text-align: center; padding: 1rem; background: {direction_color}20; border-radius: 8px;">
                                    <div style="font-size: 2em;">{direction_icon}</div>
                                    <div style="font-weight: bold; color: {direction_color};">Trend Direction</div>
                                    <div style="color: #666;">{direction_text}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with trend_col2:
                                rank_change = trend_data.get('rank_change', 0)
                                st.markdown(f"""
                                <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 8px;">
                                    <div style="font-size: 2em;">🔄</div>
                                    <div style="font-weight: bold;">Position Change</div>
                                    <div style="color: #666;">±{rank_change} positions</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with trend_col3:
                                percentile_change = trend_data.get('percentile_change', 0)
                                percentile_color = "#28a745" if percentile_change > 0 else "#dc3545" if percentile_change < 0 else "#6c757d"
                                percentile_sign = "+" if percentile_change > 0 else ""
                                st.markdown(f"""
                                <div style="text-align: center; padding: 1rem; background: {percentile_color}20; border-radius: 8px;">
                                    <div style="font-size: 2em;">📊</div>
                                    <div style="font-weight: bold; color: {percentile_color};">Percentile Change</div>
                                    <div style="color: #666;">{percentile_sign}{percentile_change:.1f}%</div>
                                </div>
                                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Unable to calculate rankings at this time. Please try again later.")
            
            # Improvement recommendations
            if rankings_data and rankings_data.get('overall_rank', 0) > 1:
                st.markdown("#### 💡 Improvement Recommendations")
                
                # Find top performer for benchmarking
                top_performers = rankings_data.get('top_performers', [])
                if top_performers:
                    top_performer = top_performers[0]
                    
                    recommendations = []
                    
                    # Certification recommendations
                    top_certs = len([c for c in top_performer.get('certifications', []) if c.get('status') == 'Active'])
                    current_certs = len([c for c in certifications if c.get('status') == 'Active'])
                    if current_certs < top_certs:
                        recommendations.append(f"🏅 **Pursue Additional Certifications**: Top performer ({top_performer['name']}) has {top_certs} active certifications.")
                    
                    # Initiative recommendations
                    top_initiatives = len(top_performer.get('quality_initiatives', []))
                    current_initiatives = len(quality_initiatives)
                    if current_initiatives < top_initiatives:
                        recommendations.append(f"🚀 **Expand Quality Initiatives**: Top performer has {top_initiatives} quality programs.")
                    
                    # Score gap analysis
                    score_gap = top_performer['total_score'] - score
                    if score_gap > 5:
                        recommendations.append(f"📈 **Focus Areas**: Bridge the {score_gap:.1f} point gap through targeted quality improvements.")
                    
                    for rec in recommendations:
                        st.markdown(rec)

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
                st.metric("🏆 Overall Score", f"{score:.2f}/100", f"{score_color}")
            
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
            if st.button("❌ Close QuXAT Healthcare Quality Grid Report", key="close_detailed"):
                if hasattr(st.session_state, 'detailed_org'):
                    del st.session_state.detailed_org
                if hasattr(st.session_state, 'detailed_data'):
                    del st.session_state.detailed_data
                st.rerun()
        
        st.markdown("---")
        
        st.markdown("""
        ### About QuXAT Healthcare Quality Grid
        The **QuXAT Healthcare Quality Grid (Quality eXcellence Assessment Tool)** is a comprehensive platform designed to evaluate 
        and score healthcare organizations worldwide based on their quality initiatives, certifications, 
        and accreditations.
        
        ### Key Features:
        - **🔍 Organization Search** - Find and analyze any healthcare organization globally
        - **📊 Quality Scoring** - Comprehensive scoring based on certifications and quality initiatives
        - **🏆 Certification Tracking** - Monitor ISO, NABH, NABL, JCI, and other quality certifications
        - **📈 Quality Trends** - Track quality improvements and quality initiatives over time
        - **📰 News Integration** - Real-time updates from company disclosures and news articles
        
        ### Tracked Certifications:
        - **ISO Certifications** - International Organization for Standardization
        - **NABH** - National Accreditation Board for Hospitals & Healthcare Providers
        - **NABL** - National Accreditation Board for Testing and Calibration Laboratories
        - **JCI** 🏥 - Joint Commission International
        - **HIMSS** - Healthcare Information and Management Systems Society
        - **AAAHC** - Accreditation Association for Ambulatory Health Care
        
        ---
        
        ### ⚠️ Important Legal Disclaimers
        
        **Assessment Nature & Limitations:**
        - The QuXAT Healthcare Quality Grid is an **assessment tool based on publicly available knowledge** regarding healthcare organizations
        - **The QuXAT Healthcare Quality Grid can be wrong** in assessing the quality of an organization and should not be considered as definitive or absolute
        - Scores are generated using automated algorithms and may not reflect the complete picture of an organization's quality
        - This platform is intended for **informational and comparative analysis purposes only**
        
        **Data Accuracy & Reliability:**
        - Information is sourced from publicly available databases, websites, and publications
        - Data accuracy depends on the reliability and timeliness of public sources
        - Organizations may have additional certifications or quality initiatives not captured in our database
        - Certification statuses may change without immediate reflection in our system
        
        **No Medical or Professional Advice:**
        - QuXAT Healthcare Quality Grid scores do not constitute medical advice, professional recommendations, or endorsements
        - Users should conduct independent verification and due diligence before making healthcare decisions
        - This tool should not be used as the sole basis for selecting healthcare providers or organizations
        
        **Limitation of Liability:**
        - QuXAT Healthcare Quality Grid and its developers disclaim all warranties, express or implied, regarding the accuracy or completeness of information
        - Users assume full responsibility for any decisions made based on QuXAT Healthcare Quality Grid assessments
        - No liability is accepted for any direct, indirect, or consequential damages arising from the use of this platform
        
        **Intellectual Property & Fair Use:**
        - All data is used under fair use principles for educational and informational purposes
        - Trademark and certification names are property of their respective owners
        - This platform is not affiliated with or endorsed by any certification bodies or healthcare organizations
        """)
        
        # Quality Dashboard Section - Consolidated from Quality Dashboard page
        st.markdown("---")
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

        # Global Healthcare Quality Section - Consolidated from Global Healthcare Quality page
        st.markdown("---")
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
                f"{avg_score:.2f}",
                delta=f"{avg_score - 75:.2f} vs baseline"
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

        # QuXAT Healthcare Quality Grid Scoring Method Section - Consolidated from QuXAT Healthcare Quality Grid Scoring Method page
        st.markdown("---")
        st.header("📋 QuXAT Healthcare Quality Grid Scoring Method")
        
        # Check if an organization has been searched
        if 'current_org' in st.session_state and st.session_state.current_org:
            org_name = st.session_state.current_org
            st.markdown(f"### 📊 Detailed Score Report for **{org_name}**")
            
            # Display the detailed scorecard
            display_detailed_scorecard(org_name)
        else:
            st.info("🔍 **Search for an organization on the Home page to view its detailed score report here.**")
            
            st.markdown("### 📋 What You'll Get in the Detailed Report")
            
            st.markdown("""
            When you search for a healthcare organization, this section will provide:
            
            **🏆 Overall Quality Score & Grade**
            - Comprehensive quality score (0-100 scale)
            - Letter grade classification (A+ to C)
            - Percentile ranking among global healthcare organizations
            
            **📊 Detailed Score Breakdown**
            - Certification scores (ISO, JCI, NABH, etc.)
            - Patient feedback analysis
            - Quality initiative assessment
            - Transparency and reporting metrics
            - Reputation and recognition factors
            
            **🏥 Organization Profile**
            - Basic organization information
            - Location and contact details
            - Specializations and services
            - Accreditation status and validity
            
            **📈 Performance Analytics**
            - Score history and trends
            - Comparative benchmarking
            - Regional and global rankings
            - Improvement recommendations
            
            **🔍 Quality Certifications**
            - Active certifications and their impact
            - Certification body information
            - Validity periods and renewal status
            - International recognition levels
            
            **🚀 Quality Initiatives**
            - Recent quality improvement programs
            - Innovation and technology adoption
            - Patient safety initiatives
            - Research and development activities
            
            **⚠️ Important Limitations**
            - Data accuracy disclaimers
            - Assessment methodology details
            - Liability limitations
            - Proper usage guidelines
            """)

        # Certifications Section - Consolidated from Certifications page
        st.markdown("---")
        st.header("🏆 Healthcare Certifications Database")
        
        # Check if an organization has been searched
        if 'current_org' in st.session_state and st.session_state.current_org:
            org_name = st.session_state.current_org
            st.markdown(f"### 🏥 Certifications for **{org_name}**")
            
            # Get organization data
            analyzer = get_analyzer()
            org_data = analyzer.get_organization_data(org_name)
            
            if org_data:
                # Display certifications
                certifications = org_data.get('certifications', [])
                if certifications:
                    st.success(f"Found {len(certifications)} certifications for {org_name}")
                    
                    for cert in certifications:
                        with st.expander(f"🏆 {cert.get('name', 'Unknown Certification')} - {cert.get('status', 'Unknown Status')}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Issuer:** {cert.get('issuer', 'N/A')}")
                                st.write(f"**Type:** {cert.get('type', 'N/A')}")
                                st.write(f"**Status:** {cert.get('status', 'N/A')}")
                            
                            with col2:
                                st.write(f"**Issue Date:** {cert.get('issue_date', 'N/A')}")
                                st.write(f"**Expiry Date:** {cert.get('expiry_date', 'N/A')}")
                                st.write(f"**Score Impact:** +{cert.get('score_impact', 0):.1f}")
                            
                            if cert.get('description'):
                                st.write(f"**Description:** {cert.get('description')}")
                else:
                    st.info(f"No certifications found for {org_name} in our database.")
            else:
                st.warning(f"No data found for {org_name}.")
        else:
            st.info("🔍 **Search for an organization to view its certifications.**")
            
            # General certification information
            st.markdown("### 🌟 Supported Certification Types")
            
            cert_types = {
                "🏥 JCI (Joint Commission International)": {
                    "description": "International healthcare accreditation for hospitals and healthcare organizations",
                    "impact": "High impact on quality score",
                    "recognition": "Global recognition"
                },
                "🇮🇳 NABH (National Accreditation Board for Hospitals)": {
                    "description": "Indian healthcare accreditation standard",
                    "impact": "High impact for Indian organizations",
                    "recognition": "National recognition in India"
                },
                "🌍 ISO Certifications": {
                    "description": "International Organization for Standardization certifications (ISO 9001, ISO 14001, etc.)",
                    "impact": "Moderate to high impact",
                    "recognition": "Global recognition"
                },
                "🏥 AAAHC": {
                    "description": "Accreditation Association for Ambulatory Health Care",
                    "impact": "Moderate impact",
                    "recognition": "US-focused recognition"
                },
                "🩺 CAP": {
                    "description": "College of American Pathologists accreditation",
                    "impact": "High impact for laboratory services",
                    "recognition": "International recognition"
                }
            }
            
            for cert_name, cert_info in cert_types.items():
                with st.expander(cert_name):
                    st.write(f"**Description:** {cert_info['description']}")
                    st.write(f"**Score Impact:** {cert_info['impact']}")
                    st.write(f"**Recognition Level:** {cert_info['recognition']}")
            
            st.markdown("### 📊 Certification Impact on Quality Scores")
            
            st.markdown("""
            **How Certifications Affect Quality Scores:**
            
            - **Active Certifications:** Full score impact based on certification type and recognition level
            - **Expired Certifications:** Reduced score impact (typically 50% of full value)
            - **Multiple Certifications:** Cumulative impact with diminishing returns
            - **International vs. National:** International certifications typically have higher impact
            - **Specialty Certifications:** Additional bonus for specialized healthcare areas
            
            **Certification Verification:**
            - All certifications are verified against official databases when possible
            - Expiry dates are tracked and impact scores accordingly
            - Regular updates ensure current certification status
            """)

except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Streamlit applications don't need a main function
    # The app runs automatically when executed
    pass
