import streamlit as st
import pandas as pd
import numpy as np
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

# Sidebar navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.selectbox("Choose a page:", 
                           ["Home", "Data Analysis", "Scoring", "Settings"])

# Main content based on page selection
try:
    if page == "Home":
        st.header("🏠 Welcome to QuXAT Scoring Dashboard")
        
        st.markdown("""
        ### 📋 About QuXAT
        The **QuXAT (Quality Assessment Tool)** is designed to help educators and administrators 
        track and analyze student performance data efficiently.
        
        ### 🎯 Key Features:
        - **📊 Interactive Dashboards** - Visualize student performance data
        - **📈 Trend Analysis** - Track progress over time  
        - **✏️ Easy Scoring** - Streamlined grading interface
        - **⚙️ Customizable Settings** - Adapt to your needs
        """)
        
        # Sample data for demonstration
        sample_data = pd.DataFrame({
            'Score Range': ['90-100', '80-89', '70-79', '60-69', '50-59'],
            'Count': [25, 45, 30, 15, 5]
        })
        
        st.subheader("📊 Sample Performance Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Score Distribution")
            # Using native Streamlit bar chart instead of Plotly
            st.bar_chart(sample_data.set_index('Score Range')['Count'])
        
        with col2:
            st.subheader("📋 Score Summary")
            # Display data as metrics instead of pie chart
            for idx, row in sample_data.iterrows():
                st.metric(
                    label=f"Score Range: {row['Score Range']}", 
                    value=f"{row['Count']} students"
                )

    elif page == "Data Analysis":
        st.header("📈 Data Analysis")
        
        # Sample time series data
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        scores = np.random.normal(75, 10, 30)
        time_data = pd.DataFrame({'Date': dates, 'Average Score': scores})
        
        st.subheader("📊 Score Trends Over Time")
        # Using native Streamlit line chart instead of Plotly
        st.line_chart(time_data.set_index('Date')['Average Score'])
        
        st.subheader("📋 Raw Data")
        st.dataframe(time_data, use_container_width=True)

    elif page == "Scoring":
        st.header("✏️ Student Scoring")
        
        st.markdown("### 📝 Quick Score Entry")
        
        col1, col2 = st.columns(2)
        
        with col1:
            student_name = st.text_input("👤 Student Name")
            assignment = st.selectbox("📚 Assignment", 
                                    ["Quiz 1", "Quiz 2", "Midterm", "Final", "Project"])
        
        with col2:
            score = st.number_input("📊 Score", min_value=0, max_value=100, value=85)
            date = st.date_input("📅 Date", datetime.now())
        
        if st.button("💾 Save Score"):
            if student_name:
                st.success(f"✅ Score saved for {student_name}: {score}/100 on {assignment}")
                
                # Display saved entry
                st.info(f"📋 **Entry Details:**\n- Student: {student_name}\n- Assignment: {assignment}\n- Score: {score}/100\n- Date: {date}")
            else:
                st.error("❌ Please enter a student name")
        
        st.markdown("---")
        st.markdown("### 📊 Recent Entries")
        
        # Sample recent entries
        recent_data = pd.DataFrame({
            'Student': ['Alice Johnson', 'Bob Smith', 'Carol Davis'],
            'Assignment': ['Quiz 1', 'Midterm', 'Quiz 2'],
            'Score': [92, 78, 85],
            'Date': ['2024-01-15', '2024-01-14', '2024-01-13']
        })
        
        st.dataframe(recent_data, use_container_width=True)

    elif page == "Settings":
        st.header("⚙️ Settings")
        
        st.markdown("### 🎨 Display Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            theme = st.selectbox("🎨 Theme", ["Light", "Dark", "Auto"])
            show_grid = st.checkbox("📊 Show Grid Lines", value=True)
            
        with col2:
            default_view = st.selectbox("🏠 Default Page", 
                                      ["Home", "Data Analysis", "Scoring"])
            auto_save = st.checkbox("💾 Auto-save Entries", value=True)
        
        st.markdown("### 📊 Scoring Settings")
        
        col3, col4 = st.columns(2)
        
        with col3:
            max_score = st.number_input("📈 Maximum Score", min_value=50, max_value=200, value=100)
            passing_grade = st.number_input("✅ Passing Grade", min_value=0, max_value=max_score, value=60)
            
        with col4:
            grade_scale = st.selectbox("📏 Grading Scale", 
                                     ["Standard (A-F)", "Numerical (0-100)", "Pass/Fail"])
            round_scores = st.checkbox("🔢 Round Scores", value=True)
        
        if st.button("💾 Save Settings"):
            st.success("✅ Settings saved successfully!")
            st.balloons()

except Exception as e:
    st.error(f"❌ An error occurred: {str(e)}")
    st.info("🔄 Please refresh the page or contact support if the issue persists.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>📊 QuXAT Scoring Dashboard v2.0 | Built with Streamlit</p>
    <p>🚀 No external chart dependencies - Pure Streamlit implementation</p>
</div>
""", unsafe_allow_html=True)