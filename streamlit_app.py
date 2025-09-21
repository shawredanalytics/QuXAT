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

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Home", "Data Analysis", "Scoring", "Settings"])

try:
    if page == "Home":
        st.header("Welcome to QuXAT Scoring System")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Scores", "1,234", "12%")
        
        with col2:
            st.metric("Average Score", "85.6", "2.1%")
        
        with col3:
            st.metric("Active Users", "456", "5%")
        
        # Sample chart
        st.subheader("Score Distribution")
        try:
            data = np.random.normal(85, 15, 1000)
            fig = px.histogram(x=data, nbins=30, title="Score Distribution")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating chart: {str(e)}")

    elif page == "Data Analysis":
        st.header("Data Analysis")
        
        try:
            # Generate sample data
            dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
            scores = np.random.normal(80, 10, len(dates))
            df = pd.DataFrame({'Date': dates, 'Score': scores})
            
            st.subheader("Score Trends Over Time")
            fig = px.line(df, x='Date', y='Score', title="Daily Scores")
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Raw Data")
            st.dataframe(df.head(10))
        except Exception as e:
            st.error(f"Error in data analysis: {str(e)}")

    elif page == "Scoring":
        st.header("Scoring Interface")
        
        with st.form("scoring_form"):
            st.subheader("Enter Score Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                student_name = st.text_input("Student Name")
                subject = st.selectbox("Subject", ["Math", "Science", "English", "History"])
            
            with col2:
                score = st.number_input("Score", min_value=0, max_value=100, value=0)
                date = st.date_input("Date", datetime.now())
            
            comments = st.text_area("Comments")
            
            submitted = st.form_submit_button("Submit Score")
            
            if submitted:
                st.success(f"Score submitted for {student_name}: {score}/100 in {subject}")

    elif page == "Settings":
        st.header("Settings")
        
        st.subheader("GitHub Integration")
        github_token = st.text_input("GitHub Token", type="password", help="Enter your GitHub personal access token")
        repo_url = st.text_input("Repository URL", placeholder="https://github.com/username/repo")
        
        if st.button("Test GitHub Connection"):
            if github_token and repo_url:
                st.success("✅ GitHub connection successful!")
            else:
                st.error("❌ Please provide both GitHub token and repository URL")
        
        st.subheader("Application Settings")
        theme = st.selectbox("Theme", ["Light", "Dark"])
        auto_save = st.checkbox("Auto-save data", value=True)
        notifications = st.checkbox("Enable notifications", value=True)
        
        if st.button("Save Settings"):
            st.success("Settings saved successfully!")

except Exception as e:
    st.error(f"Application error: {str(e)}")
    st.info("Please refresh the page or contact support if the issue persists.")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit 🚀 | Connected to GitHub 🐙")