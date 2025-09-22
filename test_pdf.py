#!/usr/bin/env python3
"""
Test script to debug PDF generation functionality
"""

import sys
import os
import traceback
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pdf_generation():
    """Test the PDF generation function directly"""
    
    print("🔍 Testing PDF Generation Function...")
    print("=" * 50)
    
    try:
        # Import required modules
        print("📦 Importing modules...")
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        import io
        print("✅ All PDF modules imported successfully")
        
        # Test basic PDF creation
        print("\n📄 Testing basic PDF creation...")
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        # Create sample content
        styles = getSampleStyleSheet()
        story = []
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        story.append(Paragraph("QuXAT Test PDF Report", title_style))
        story.append(Spacer(1, 12))
        
        # Add content
        story.append(Paragraph("This is a test PDF generated to verify functionality.", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Add test data table
        test_data = [
            ['Metric', 'Value', 'Status'],
            ['PDF Generation', 'Working', '✅'],
            ['ReportLab', 'Installed', '✅'],
            ['Test Date', datetime.now().strftime('%Y-%m-%d %H:%M'), '✅']
        ]
        
        table = Table(test_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        
        # Build PDF
        print("🔨 Building PDF document...")
        doc.build(story)
        
        # Get PDF data
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        print(f"✅ PDF generated successfully! Size: {len(pdf_data)} bytes")
        
        # Save test PDF to file
        test_filename = f"test_pdf_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(test_filename, 'wb') as f:
            f.write(pdf_data)
        
        print(f"💾 Test PDF saved as: {test_filename}")
        
        return pdf_data, None
        
    except Exception as e:
        error_msg = f"❌ Error in PDF generation: {str(e)}"
        print(error_msg)
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        return None, str(e)

def test_streamlit_pdf_function():
    """Test the actual Streamlit PDF function"""
    
    print("\n🎯 Testing Streamlit PDF Function...")
    print("=" * 50)
    
    try:
        # Import the streamlit app module
        print("📦 Importing streamlit_app module...")
        import streamlit_app
        print("✅ Streamlit app module imported successfully")
        
        # Create sample organization data
        sample_org_data = {
            'name': 'Test Healthcare Organization',
            'location': 'Test City, Test Country',
            'certifications': [
                {'name': 'ISO 9001:2015', 'status': 'Active', 'valid_until': '2025-12-31', 'score_impact': 15},
                {'name': 'ISO 14001:2015', 'status': 'Active', 'valid_until': '2025-12-31', 'score_impact': 12},
                {'name': 'NABH', 'status': 'Active', 'valid_until': '2026-06-30', 'score_impact': 25}
            ],
            'quality_initiatives': [
                {'title': 'Patient Safety Program', 'year': '2024'},
                {'title': 'Digital Health Initiative', 'year': '2023'}
            ],
            'scores': {
                'overall': 85,
                'certifications': 90,
                'quality_initiatives': 80,
                'transparency': 75,
                'reputation': 85
            }
        }
        
        print("🏥 Testing with sample organization data...")
        print(f"   Organization: {sample_org_data['name']}")
        print(f"   Location: {sample_org_data['location']}")
        print(f"   Overall Score: {sample_org_data['scores']['overall']}")
        
        # Test the PDF generation function
        print("\n🔨 Calling generate_detailed_scorecard_pdf function...")
        pdf_data = streamlit_app.generate_detailed_scorecard_pdf(
            sample_org_data['name'], 
            sample_org_data
        )
        
        if pdf_data:
            print(f"✅ Streamlit PDF function successful! Size: {len(pdf_data)} bytes")
            
            # Save the PDF
            test_filename = f"streamlit_test_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(test_filename, 'wb') as f:
                f.write(pdf_data)
            
            print(f"💾 Streamlit test PDF saved as: {test_filename}")
            return pdf_data, None
        else:
            error_msg = "❌ Streamlit PDF function returned None"
            print(error_msg)
            return None, error_msg
            
    except Exception as e:
        error_msg = f"❌ Error testing Streamlit PDF function: {str(e)}"
        print(error_msg)
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        return None, str(e)

if __name__ == "__main__":
    print("🧪 QuXAT PDF Generation Test Suite")
    print("=" * 60)
    
    # Test 1: Basic PDF generation
    basic_pdf, basic_error = test_pdf_generation()
    
    # Test 2: Streamlit PDF function
    streamlit_pdf, streamlit_error = test_streamlit_pdf_function()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Basic PDF Generation: {'✅ PASS' if basic_pdf else '❌ FAIL'}")
    if basic_error:
        print(f"   Error: {basic_error}")
    
    print(f"Streamlit PDF Function: {'✅ PASS' if streamlit_pdf else '❌ FAIL'}")
    if streamlit_error:
        print(f"   Error: {streamlit_error}")
    
    if basic_pdf and streamlit_pdf:
        print("\n🎉 All tests passed! PDF generation is working correctly.")
        print("💡 The issue might be in the Streamlit UI interaction or button handling.")
    elif basic_pdf and not streamlit_pdf:
        print("\n⚠️  Basic PDF works but Streamlit function fails.")
        print("💡 Check the Streamlit PDF function implementation.")
    elif not basic_pdf:
        print("\n❌ Basic PDF generation failed.")
        print("💡 Check ReportLab installation and dependencies.")
    
    print("\n🔍 Next steps:")
    print("1. Check the generated test PDF files")
    print("2. Review any error messages above")
    print("3. Test the actual Streamlit app button interaction")