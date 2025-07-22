import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import geopandas as gpd
import pycountry
from datetime import datetime
import os

# Initialize session state for data storage with a unique key
if 'hr_survey_data' not in st.session_state:
    st.session_state.hr_survey_data = pd.DataFrame(columns=[
        'timestamp', 'location', 'department', 
        'hiring_time', 'fair_strategies', 'rehire', 'payment_negotiation'
    ])
    # Load existing data immediately upon first visit
    if os.path.exists('hr_survey_data.csv'):
        st.session_state.hr_survey_data = pd.read_csv('hr_survey_data.csv')

# Function to save survey data and update dashboard
def save_survey(location, department, hiring_time, fair_strategies, rehire, payment_negotiation):
    new_entry = {
        'timestamp': datetime.now(),
        'location': location,
        'department': department,
        'hiring_time': hiring_time,
        'fair_strategies': ", ".join(fair_strategies) if isinstance(fair_strategies, list) else fair_strategies,
        'rehire': rehire,
        'payment_negotiation': payment_negotiation
    }
    
    # Convert to DataFrame and append
    new_df = pd.DataFrame([new_entry])
    st.session_state.hr_survey_data = pd.concat([st.session_state.hr_survey_data, new_df], ignore_index=True)
    
    # Save to CSV (overwrite entire file to maintain consistency)
    st.session_state.hr_survey_data.to_csv('hr_survey_data.csv', index=False)
    st.success("Thank you for completing the survey!")

def show_hr_survey():
    st.title("HR Hiring Practices for Gig Workers: Survey")
    
    with st.form("hr_survey_form"):
        # Location input
        country_names = [country.name for country in pycountry.countries]
        location = st.selectbox("Select your location/country:", sorted(country_names))
        
        # Department selection
        departments = [
            "Recruitment", "Training", "Onboarding", "Hiring", 
            "Compensation", "Employee Relations", "Talent Management"
        ]
        department = st.selectbox("Select your HR department:", departments)
        
        # Question 1: Hiring time
        hiring_time = st.select_slider(
            "1. How long does your organization typically take to hire gig workers?",
            options=["Less than 1 week", "1-2 weeks", "2-4 weeks", "1-2 months", "More than 2 months"]
        )
        
        # Question 2: Fair hiring strategies
        fair_strategies = st.multiselect(
            "2. What strategies does your organization use to make the gig-worker's hiring process fair? (Select all that apply)",
            options=[
                "Blind resume screening",
                "Structured interviews",
                "Diverse hiring panels",
                "Skills-based assessments",
                "Standardized evaluation criteria",
                "Bias training for interviewers",
                "Other"
            ]
        )
        
        # Question 3: Re-hiring
        rehire = st.radio(
            "3. Does your organization actively re-hire former gig workers?",
            options=["Yes, frequently", "Occasionally", "Rarely", "Never"]
        )
        
        # Question 4: Payment negotiation
        payment_negotiation = st.selectbox(
            "4. How does your organization typically negotiate with gig workers and decide on their payment?",
            options=[
                "Fixed salary bands with no negotiation",
                "Negotiation based on candidate's current salary",
                "Negotiation based on market rates",
                "Negotiation based on skills assessment",
                "Other approach"
            ]
        )
        
        submitted = st.form_submit_button("Submit Survey")
        
        if submitted:
            save_survey(location, department, hiring_time, fair_strategies, rehire, payment_negotiation)
            # Automatically show the dashboard after submission
            st.rerun()

def show_hr_dashboard():
    st.title("Survey Results: Gig-Hiring Practices Around The Globe")
    
    # Always show the dashboard, even with empty data
    if st.session_state.hr_survey_data.empty:
        st.warning("No survey data available yet. Please complete the survey to see analytics.")
        return
    
    # Display basic stats
    st.subheader("Survey Responses Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Responses", len(st.session_state.hr_survey_data))
    col2.metric("Unique Countries", st.session_state.hr_survey_data['location'].nunique())
    col3.metric("Departments Represented", st.session_state.hr_survey_data['department'].nunique())
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Location distribution
        st.subheader("Respondent Locations")
        country_counts = st.session_state.hr_survey_data['location'].value_counts().reset_index()
        country_counts.columns = ['Country', 'Count']
        
        try:
            # Try to plot a map (may not work in all environments)
            url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"

            world = gpd.read_file(url)
            # world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
            merged = world.set_index('name').join(country_counts.set_index('Country'))
            
            fig, ax = plt.subplots(figsize=(10, 6))
            merged.plot(column='Count', ax=ax, legend=True,
                        missing_kwds={"color": "lightgrey"},
                        cmap='Blues')
            plt.title('Respondent Locations')
            st.pyplot(fig)
        except Exception as e:
            # st.warning(f"Map visualization unavailable: {str(e)}")
            st.bar_chart(country_counts.set_index('Country'))
        
        # Fair strategies analysis
        st.subheader("Fair Hiring Strategies Used")
        if 'fair_strategies' in st.session_state.hr_survey_data.columns:
            all_strategies = []
            for strategies in st.session_state.hr_survey_data['fair_strategies']:
                if pd.notna(strategies) and isinstance(strategies, str):
                    all_strategies.extend([s.strip() for s in strategies.split(',')])
            
            if all_strategies:
                strategy_counts = pd.Series(all_strategies).value_counts().reset_index()
                # st.bar_chart(strategy_counts) #, color = ["#2d00f7","#6a00f4","#8900f2","#bc00dd","#e500a4","#f20089","#ffb600"])
                strategy_counts.columns = ['Strategy', 'Count']
            
                colors = ["#ea6016","#f3712b","#f58b51","#f0e3dd","#fc9cb5","#fa4274","#df3764"]
                
                fig = px.bar(strategy_counts, x='Strategy', y='Count',
                            color='Strategy',
                            color_discrete_sequence=colors[:len(strategy_counts)],
                            )
                
                fig.update_traces(textposition='outside')
                fig.update_layout(
                    xaxis_title='Strategy',
                    yaxis_title='Frequency',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No strategies data available")
            
        # Payment negotiation analysis
        st.subheader("Approaches for Payment Negotiation with Gig Workers")
        if 'payment_negotiation' in st.session_state.hr_survey_data.columns:
            payment_counts = st.session_state.hr_survey_data['payment_negotiation'].value_counts().reset_index()
            payment_counts.columns = ['Payment-Negotiation', 'Count']
            
            colors = ["#ff1b6b","#e03884","#c1559c","#a273b5","#8390ce","#64ade6","#45caff"]
            fig = px.bar(payment_counts, x='Payment-Negotiation', y='Count',
                            color='Payment-Negotiation',
                            color_discrete_sequence=colors[:len(payment_counts)],
                            )
            fig.update_traces(textposition='outside')
            fig.update_layout(
                xaxis_title='Payment-Negotiation',
                yaxis_title='Frequency',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            # st.bar_chart(payment_counts) #, color = ["#40c9ff","#5cacff","#788fff","#9473ff","#b056ff","#cc39ff","#e81cff"])
        else:
            st.warning("No payment negotiation data available")
    
    with col2:   
        # Department distribution
        st.subheader("Department Distribution")
        if st.session_state.hr_survey_data['department'].nunique() > 0:
            colors = ["#5de0f0","#77d6f1","#90cdf2","#aac3f3","#c4b9f3","#ddb0f4","#f7a6f5"]
            dept_counts = st.session_state.hr_survey_data['department'].value_counts().reset_index()
            dept_counts.columns = ['Departments', 'Count']
            
            fig = px.bar(dept_counts, x='Departments', y='Count',
                            color='Departments',
                            color_discrete_sequence=colors[:len(dept_counts)],
                            )
            fig.update_traces(textposition='outside')
            fig.update_layout(
                xaxis_title='Participation of HR Departments in the Survey',
                yaxis_title='Frequency',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No department data available")
    
        # Hiring time analysis
        st.subheader("Hiring Time Analysis")
        if 'hiring_time' in st.session_state.hr_survey_data.columns:
            hiring_time_order = ["Less than 1 week", "1-2 weeks", "2-4 weeks", "1-2 months", "More than 2 months"]
            hiring_counts = st.session_state.hr_survey_data['hiring_time'].value_counts().reindex(hiring_time_order).reset_index()
            hiring_counts.columns = ['Hiring_Time', 'Count']
            
            colors = ["#ff0f7b","#fd3e60","#fc5552","#fa6c44","#f89b29"]
            fig = px.bar(hiring_counts, x='Hiring_Time', y='Count',
                            color='Hiring_Time',
                            color_discrete_sequence=colors[:len(hiring_counts)],
                            )
            fig.update_traces(textposition='outside')
            fig.update_layout(
                xaxis_title='Global Average Hiring Time For Gig Workers',
                yaxis_title='Frequency',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # st.bar_chart(hiring_counts)
        else:
            st.warning("No hiring time data available")
    
        # Rehire analysis
        st.subheader("Organizational Policies on Re-Hiring Former Gig Workers")
        if 'rehire' in st.session_state.hr_survey_data.columns:
            rehire_order = ["Yes, frequently", "Occasionally", "Rarely", "Never"]
            rehire_counts = st.session_state.hr_survey_data['rehire'].value_counts().reindex(rehire_order).reset_index()
            rehire_counts.columns = ['Rehire-Decision', 'Count']
            
            colors = ["#fff1bf","#f69ba6", "#ef6295","#ec458d"]
            fig = px.bar(rehire_counts, x='Rehire-Decision', y='Count',
                            color='Rehire-Decision',
                            color_discrete_sequence=colors[:len(rehire_counts)],
                            )
            fig.update_traces(textposition='outside')
            fig.update_layout(
                xaxis_title='Rehire-Decision',
                yaxis_title='Frequency',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            # st.bar_chart(rehire_counts) #, color = ["#fff1bf","#f69ba6", "#ef6295","#ec458d"])
        else:
            st.warning("No rehire data available")
    
    
    
    # # Raw data
    # if st.checkbox("Show raw data"):
    #     st.write(st.session_state.hr_survey_data)

def hr_survey_page():
    """Main function to be called from your app's navigation"""
    tab1, tab2 = st.tabs(["📝 Take Survey", "📊 Survey Results"])
    
    with tab1:
        show_hr_survey()
        
    with tab2:
        show_hr_dashboard()
        
        
# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# import geopandas as gpd
# import pycountry
# from datetime import datetime
# import os

# # Initialize session state for data storage if not already present
# if 'hr_survey_data' not in st.session_state:
#     st.session_state.hr_survey_data = pd.DataFrame(columns=[
#         'timestamp', 'location', 'department', 
#         'hiring_time', 'fair_strategies', 'rehire', 'payment_negotiation'
#     ])

# # Function to save survey data
# def save_survey(location, department, hiring_time, fair_strategies, rehire, payment_negotiation):
#     new_entry = {
#         'timestamp': datetime.now(),
#         'location': location,
#         'department': department,
#         'hiring_time': hiring_time,
#         'fair_strategies': fair_strategies,
#         'rehire': rehire,
#         'payment_negotiation': payment_negotiation
#     }
    
#     # Convert to DataFrame and append
#     new_df = pd.DataFrame([new_entry])
#     st.session_state.hr_survey_data = pd.concat([st.session_state.hr_survey_data, new_df], ignore_index=True)
    
#     # Save to CSV
#     if not os.path.exists('hr_survey_data.csv'):
#         st.session_state.hr_survey_data.to_csv('hr_survey_data.csv', index=False)
#     else:
#         st.session_state.hr_survey_data.to_csv('hr_survey_data.csv', mode='a', header=False, index=False)

# # Function to load existing data
# @st.cache_data
# def load_hr_data():
#     if os.path.exists('hr_survey_data.csv'):
#         return pd.read_csv('hr_survey_data.csv')
#     return pd.DataFrame()

# def show_hr_survey():
#     st.title("HR Hiring Practices For Gig Workers: Survey")
    
#     with st.form("hr_survey_form"):
#         # Location input
#         country_names = [country.name for country in pycountry.countries]
#         location = st.selectbox("Select your location/country:", sorted(country_names))
        
#         # Department selection
#         departments = [
#             "Recruitment", "Training", "Onboarding", "Hiring", 
#             "Compensation", "Employee Relations", "Talent Management"
#         ]
#         department = st.selectbox("Select your HR department:", departments)
        
#         # Question 1: Hiring time
#         hiring_time = st.select_slider(
#             "1. How long does your organization typically take to hire gig workers?",
#             options=["Less than 1 week", "1-2 weeks", "2-4 weeks", "1-2 months", "More than 2 months"]
#         )
        
#         # Question 2: Fair hiring strategies
#         fair_strategies = st.multiselect(
#             "2. What strategies does your organization use to make the hiring process fair? (Select all that apply)",
#             options=[
#                 "Blind resume screening",
#                 "Structured interviews",
#                 "Diverse hiring panels",
#                 "Skills-based assessments",
#                 "Standardized evaluation criteria",
#                 "Bias training for interviewers",
#                 "Other"
#             ]
#         )
        
#         # Question 3: Re-hiring
#         rehire = st.radio(
#             "3. Does your organization actively re-hire former gig workers?",
#             options=["Yes, frequently", "Occasionally", "Rarely", "Never"]
#         )
        
#         # Question 4: Payment negotiation
#         payment_negotiation = st.selectbox(
#             "4. How does your organization typically negotiate with gig workers and decide on payment?",
#             options=[
#                 "Fixed salary bands with no negotiation",
#                 "Negotiation based on candidate's current payments",
#                 "Negotiation based on market rates",
#                 "Negotiation based on skills assessment",
#                 "Other approach"
#             ]
#         )
        
#         submitted = st.form_submit_button("Submit Survey")
        
#         if submitted:
#             save_survey(location, department, hiring_time, ", ".join(fair_strategies), rehire, payment_negotiation)
#             st.success("Thank you for completing the survey!")

# def show_hr_dashboard():
#     st.title("HR Hiring Practices For Gig Workers: Survey Results")
#     existing_data = load_hr_data()
#     # # Load data if not in session state
#     # if st.session_state.hr_survey_data.empty:
#     #     existing_data = load_hr_data()
#     #     if not existing_data.empty:
#     #         st.session_state.hr_survey_data = existing_data
    
#     # if st.session_state.hr_survey_data.empty:
#     #     st.warning("No survey data available yet. Please complete the survey first.")
#     # return
        
    
#     # Display basic stats
#     st.subheader("Survey Responses Overview")
#     col1, col2, col3 = st.columns(3)
#     col1.metric("Total Responses", len(st.session_state.hr_survey_data))
#     col2.metric("Unique Countries", st.session_state.hr_survey_data['location'].nunique())
#     col3.metric("Departments Represented", st.session_state.hr_survey_data['department'].nunique())
    
#     # Location distribution
#     st.subheader("Respondent Locations")
#     country_counts = st.session_state.hr_survey_data['location'].value_counts().reset_index()
#     country_counts.columns = ['Country', 'Count']
    
#     try:
#         # Try to plot a map (may not work in all environments)
#         world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
#         merged = world.set_index('name').join(country_counts.set_index('Country'))
        
#         fig, ax = plt.subplots(figsize=(10, 6))
#         merged.plot(column='Count', ax=ax, legend=True,
#                     missing_kwds={"color": "lightgrey"},
#                     cmap='Blues')
#         plt.title('Respondent Locations')
#         st.pyplot(fig)
#     except:
#         # Fallback to bar chart if map doesn't work
#         st.bar_chart(country_counts.set_index('Country'))
    
#     # Department distribution
#     st.subheader("Department Distribution")
#     dept_counts = st.session_state.hr_survey_data['department'].value_counts()
#     fig, ax = plt.subplots()
#     dept_counts.plot(kind='pie', autopct='%.0f%%', textprops={'size': 'smaller'}, radius=0.5, ax=ax)
#     ax.set_ylabel('')
#     st.pyplot(fig)
    
#     # Hiring time analysis
#     st.subheader("Hiring Time Analysis")
#     hiring_time_order = ["Less than 1 week", "1-2 weeks", "2-4 weeks", "1-2 months", "More than 2 months"]
#     hiring_counts = st.session_state.hr_survey_data['hiring_time'].value_counts().reindex(hiring_time_order)
#     st.bar_chart(hiring_counts)
    
#     # Fair strategies analysis
#     st.subheader("Fair Hiring Strategies Used")
#     # Split multi-select answers and count occurrences
#     all_strategies = []
#     for strategies in st.session_state.hr_survey_data['fair_strategies']:
#         if isinstance(strategies, str):
#             all_strategies.extend([s.strip() for s in strategies.split(',')])
    
#     strategy_counts = pd.Series(all_strategies).value_counts()
#     st.bar_chart(strategy_counts)
    
#     # Rehire analysis
#     st.subheader("Re-Hiring Practices")
#     rehire_order = ["Yes, frequently", "Occasionally", "Rarely", "Never"]
#     rehire_counts = st.session_state.hr_survey_data['rehire'].value_counts().reindex(rehire_order)
#     st.bar_chart(rehire_counts)
    
#     # Payment negotiation analysis
#     st.subheader("Payment Negotiation Approaches")
#     payment_counts = st.session_state.hr_survey_data['payment_negotiation'].value_counts()
#     st.bar_chart(payment_counts)
    
#     # Raw data
#     if st.checkbox("Show raw data"):
#         st.write(st.session_state.hr_survey_data)

