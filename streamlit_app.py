import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="QuXAT Scoring Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("📊 QuXAT Scoring Dashboard")
st.markdown("---")

try:
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Home", "Data Analysis", "Scoring", "Settings"])

    if page == "Home":
        st.header("🏠 Welcome to QuXAT Scoring Dashboard")
        
        # Create sample metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Students", "156", "12")
        with col2:
            st.metric("Average Score", "78.5", "2.3")
        with col3:
            st.metric("Pass Rate", "89%", "5%")
        with col4:
            st.metric("Completion Rate", "94%", "1%")
        
        st.markdown("---")
        
        # Sample data for visualization
        sample_data = pd.DataFrame({
            'Score Range': ['0-20', '21-40', '41-60', '61-80', '81-100'],
            'Count': [5, 12, 28, 67, 44]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Score Distribution")
            fig = px.bar(sample_data, x='Score Range', y='Count', 
                        title="Student Score Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🥧 Performance Overview")
            fig = px.pie(sample_data, values='Count', names='Score Range',
                        title="Score Range Distribution")
            st.plotly_chart(fig, use_container_width=True)

    elif page == "Data Analysis":
        st.header("📈 Data Analysis")
        
        # Sample time series data
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        scores = np.random.normal(75, 10, 30)
        time_data = pd.DataFrame({'Date': dates, 'Average Score': scores})
        
        st.subheader("📊 Score Trends Over Time")
        fig = px.line(time_data, x='Date', y='Average Score', 
                     title="Average Scores Trend")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 Raw Data")
        st.dataframe(time_data, use_container_width=True)

    elif page == "Scoring":
        st.header("✏️ Student Scoring")
        
        with st.form("scoring_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                student_name = st.text_input("Student Name")
                student_id = st.text_input("Student ID")
                
            with col2:
                score = st.number_input("Score", min_value=0, max_value=100, value=0)
                subject = st.selectbox("Subject", ["Mathematics", "Science", "English", "History"])
            
            comments = st.text_area("Comments")
            
            submitted = st.form_submit_button("Submit Score")
            
            if submitted:
                st.success(f"Score submitted for {student_name} (ID: {student_id})")
                st.info(f"Subject: {subject}, Score: {score}")

    elif page == "Settings":
        st.header("⚙️ Settings")
        
        st.subheader("🔗 GitHub Integration")
        st.info("This application is connected to GitHub repository: shawredanalytics/QuXAT")
        
        st.subheader("📱 Application Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("Enable notifications", value=True)
            st.checkbox("Auto-save scores", value=True)
            
        with col2:
            st.selectbox("Theme", ["Light", "Dark", "Auto"])
            st.slider("Refresh interval (seconds)", 5, 60, 30)

    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit | Connected to GitHub: shawredanalytics/QuXAT")

except Exception as e:
    st.error("An error occurred while loading the application.")
    st.error(f"Error details: {str(e)}")
    st.info("Please refresh the page or contact support if the issue persists.")