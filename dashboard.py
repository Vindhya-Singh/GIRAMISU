import streamlit as st
import pandas as pd
import plotly.express as px
import random

import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import uuid

from streamlit.components.v1 import html
from hr_survey import hr_survey_page

# Initialize Firebase only once
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
        firebase_admin.initialize_app(cred, {
            'databaseURL': st.secrets["firebase"]["databaseURL"]
        })

# Always call this before any Firebase operation
init_firebase()

# Write to Firebase Realtime Database
def submit_story_to_firebase(name, role, story):
    ref = db.reference("/stories")
    story_id = str(uuid.uuid4())
    data = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "name": name,
        "role": role,
        "story": story
    }
    ref.child(story_id).set(data)
    
# --- Stories Database (CSV Storage) ---
story_file = "stories.csv"
submitted_story_file = 'submitted_stories.csv'

def load_stories():
    try:
        return pd.read_csv(story_file)
    except FileNotFoundError:
        return pd.DataFrame(columns=["timestamp", "name", "role", "story"])

def save_story(name, role, story):
    df = load_stories()
    new_row = {"timestamp": datetime.now().date(), "name": name, "role": role, "story": story}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    open('submitted_stories.csv', 'w').write(df.to_csv(), index=False)
    # df.to_csv(submitted_story_file, index=False)

    
# --- Page Config ---
st.set_page_config(page_title="📊 GIRAMISU", layout="wide")

# --- Sidebar Navigation ---
menu = st.sidebar.radio("Navigation", ["Homepage", "Global HR Compass", "Impact Metrics Hub", "HR Voices and Sentiments", "Transparency Tracker"])

if menu == "Homepage":
    st.title("Welcome to GIRAMISU")
    st.subheader("Gig Inclusion and Responsible Action through Managerial Insight and Situated Understanding")
    st.markdown("---")

    st.subheader("🔍 What is this about?")
    st.write("Inspired by the layered harmony of tiramisu, we recognize three pillars of the gig economy: policy makers who shape the landscape, gig workers who fuel its flexibility, and HR managers who bridge the gap between structure and agility. Designed exclusively for HR leaders, GIRAMISU transforms raw insights into actionable strategies, fostering transparency in hiring practices, accountability in workforce management, and fairness in workplace climates. This is your platform to navigate the complexities of the gig economy with confidence—because inclusive growth begins with empowered decision-making.")
    st.write("Explore. Act. Lead. Because managing gig talent shouldn’t be a guessing game.")

    st.subheader("🎥 Watch an Overview Video")
    st.video("https://youtu.be/MrH0N-zluaU")  # Replace with your real video

    st.subheader("👥 HR Code of Ethics")
    st.markdown("""These fundamental principles guide ethical decision-making in Human Resources:""")
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ##### 🤝 Professionalism  
        Maintain high standards of behavior and integrity in all HR activities
        
        ##### 🔒 Trustworthiness  
        Build and maintain trust through honest, reliable actions
        
        ##### 🙏 Respect  
        Value all individuals and treat them with dignity
        """)
    
    with col2:
        st.markdown("""
        ##### 🎯 Competence  
        Maintain and develop professional knowledge and skills
        
        ##### ⚖️ Equity and Fairness
        Ensure just treatment and equal opportunities for all
        
        ##### 🔐 Confidentiality  
        Protect sensitive employee and organizational information
        
        ##### ⚖️ Legal Compliance  
        Adhere to all applicable laws and regulations
        """)

    st.subheader("📬 Contact & Feedback")
    st.write("For feedback or questions, contact: vsingh@is.mpg.de")

    st.subheader("💡 Motivation")
    st.markdown("[Read our research motivation](https://docs.google.com/document/d/1GRYIYdFG8Ene6Mb3j9hWS6I1n-lMcNzoOk-1NoE3VIg/edit?usp=sharing)")  # Replace with real link

elif menu == "Global HR Compass":
    st.title("Global HR Compass")
    st.subheader("Surfacing trends, top HRM Practices, and Discourse Topics from global HR discussions on managing gig workers.")
    st.markdown("---")
    
    # Chart customizations
    st.sidebar.header("Chart Customization: Adjust the sliders to see charts change")
    line_width = st.sidebar.slider("Line width", 1, 5, 2)
    st.sidebar.subheader("Font Sizes")
    axis_title_font_size = st.sidebar.slider("Axis title font size", 10, 20, 14)
    axis_tick_font_size = st.sidebar.slider("Axis tick font size", 8, 18, 12)
    legend_font_size = st.sidebar.slider("Legend font size", 8, 20, 12)
    # st.subheader("📊 Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Which HRM Practices are the most important for managing gig workers?**")
        data = pd.DataFrame({"Frequency": [364, 277, 251, 220, 184, 166, 166, 152, 141, 134], "HRM Practices": ["Training", "Org.Culture", "Motivation", "Leadership", "Job Design", "HRM", "Comp&Benefits", "Health and Safety", "Selection", "D&I"]})
        # st.bar_chart(data, x = "HRM Practices", y = "Frequency", horizontal = True, color = "HRM Practices")
        colors = ['#21409a','#04adff','#e48873','#f16623','#f44546','#03a8a0','#039c4b','#66d313','#fedf17','#ff0984']
        fig = px.bar(data, x='Frequency', y='HRM Practices',
                            color='HRM Practices',
                            color_discrete_sequence=colors[:len(data)],
                            )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            xaxis_title='Frequency',
            yaxis_title='HRM Practices',
            showlegend=False
        )
        fig.update_layout(
        font=dict(
            size=axis_tick_font_size  # Base font size
        ),
        xaxis=dict(
            title=dict(
                text="Frequency",
                font=dict(size=axis_title_font_size)
            ),
            tickfont=dict(size=axis_tick_font_size)
        ),
        yaxis=dict(
            title=dict(
                text="HRM Practices",
                font=dict(size=axis_title_font_size)
            ),
            tickfont=dict(size=axis_tick_font_size)
        ),
        hoverlabel=dict(
            font=dict(size=axis_tick_font_size)
        ),
    )
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("**What are the most important Discourse Topics in the global HRM disourse on managing gig workers?**")
        st.write("**How to use:** Click on See Explanation to know more about each Discourse Topic.")
        topics_data = {
            "💼 Work From Home": "Work From Home in the gig economy enables high-skilled roles to be outsourced globally, advancing gig workers up the value chain, while its flexibility particularly empowers women to participate more actively than in traditional sectors.",
            "🏢 HRM": "HRM in the gig economy must adapt by providing training, benefits, and inclusive engagement for non-permanent talent, while balancing the opportunities (global access to high-skilled roles, cost efficiency, innovation) with risks (security, competition) as gig workers increasingly become important." ,
            "🤝 Talent Management": "HR Managers in the gig economy must bridge skill gaps through targeted training for freelancers, while strategically assessing which roles suit gig-based models and retaining leadership qualities that require long-term organizational alignment.",
            "🦾 AI in Gig Economy": "AI in Gig Work is rapidly transforming labor markets by automating tasks like job description creation and enabling gig workers to find opportunities through AI-powered platforms. For gig workers, adapting to AI-driven skill demands is critical, while HR managers must integrate AI competencies into their practices to effectively recruit, manage, and support this evolving workforce",
            "🫂 Freelancers": "The number of gig workers is rising globally. They operate as freelancers and independent contractors who must navigate self-managed taxes and limited benefits, while HR adapts to integrate this agile talent pool into organizational workflows.",
            "🚕 Gig Apps": "Gig Apps are an important component of the gig economy, connecting skilled workers with organizations through platforms like Fiverr Business and Catalant, while reshaping work experiences via streamlined project matching and case study-driven models in tech, design, and beyond.",
            "⚕️ COVID": "COVID-19 redefined work for everyone including gig workers. Many employees made a shift to prioritizing freedom, work-life balance, and happiness over traditional career markers. Consequently, accelerating the shift of millennials and others to gig work as a sustainable, fulfilling alternative in the post-pandemic economy.",  
            "💱 Gig Economy": "Gig Economy engagement among HR professionals surged 50% (2018–2023), reflecting rapid adaptation to structural workforce shifts—from pandemic-driven remote work to permanent gig worker integration—as organizations redefine talent strategies for flexibility and resilience."}    

        cols = st.columns(2)  # 2-column layout
        # for i, name in enumerate(names):
        for i, (name, back_content) in enumerate(topics_data.items()):
            with cols[i % 2]:  # Alternate between columns
                st.markdown(
                    f"""
                    <div style='padding: 10px; border-radius: 5px; 
                    background-color: #888f7a; margin: 5px 0;'>
                    {name}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                with st.expander("See explanation"):
                    st.write(back_content)

    with col2:
        st.write("**HRM Practices Longitudinal Evolution**")
        # Create DataFrame from the chart data
        data = {
            "Year": ["2009", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"],
            "Compensation & Benefits": [0, 0, 1, 4, 3, 3, 7, 12, 8, 4],
            "D&I": [0, 0, 0, 2, 0, 2, 3, 3, 1, 2],
            "Health & Safety": [0, 0, 0, 0, 1, 4, 2, 5, 2, 5],
            "HRM": [1, 1, 4, 18, 7, 21, 17, 19, 12, 11],
            "Job Design": [0, 1, 2, 4, 7, 5, 4, 5, 5, 2],
            "Leadership": [0, 0, 3, 8, 12, 10, 12, 23, 9, 9],
            "Motivation": [0, 0, 0, 2, 3, 4, 6, 12, 6, 6],
            "Organization Culture": [0, 3, 3, 5, 6, 15, 10, 7, 6, 2],
            "Selection": [0, 1, 3, 6, 6, 10, 7, 8, 5, 7],
            "Training & Development": [0, 0, 3, 4, 6, 6, 9, 18, 10, 7]
        }

        df = pd.DataFrame(data)
        # Melt dataframe for Plotly (convert wide to long format)
        df_melted = df.melt(id_vars='Year', var_name='HRM Practices', value_name='Value')
        
        # Create interactive plot
        fig = px.line(
            df_melted,
            x="Year",
            y="Value",
            color="HRM Practices",
            line_shape="linear",
            width=1000,
            height=500
        )
        
        # Update line styles
        fig.update_traces(
            line=dict(width=line_width),
            marker=dict(size=8)
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title= "Percentage Occurence in the Discourse",
            legend_title="HRM Practices",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_layout(
        font=dict(
            size=axis_tick_font_size  # Base font size
        ),
        xaxis=dict(
            title=dict(
                text="Year",
                font=dict(size=axis_title_font_size)
            ),
            tickfont=dict(size=axis_tick_font_size)
        ),
        yaxis=dict(
            title=dict(
                text="Percentage Occurence in the Discourse",
                font=dict(size=axis_title_font_size)
            ),
            tickfont=dict(size=axis_tick_font_size)
        ),
        legend=dict(
            title=dict(
                text="HRM Practices",
                font=dict(size=legend_font_size)
            ),
            font=dict(size=legend_font_size)
        ),
        hoverlabel=dict(
            font=dict(size=axis_tick_font_size)
        ),
    )
        
        # Display the plot
        st.plotly_chart(fig, use_container_width=True)

        
        # Radar Chart visualising the relationship between topics and HRM practices
        data = {
                "HRM Practices": ["Compensation & Benefits", "D&I", "Health and Safety", "HRM", 
                                "Job Design", "Leadership", "Motivation", "Organizational culture",
                                "Selection", "Training & Development"],
                "Work from Home": [666, 1158, 1040, 813, 905, 826, 1188, 1157, 560, 1708],
                "Talent Management": [577, 971, 884, 658, 748, 791, 987, 1079, 484, 1524],
                "HRM": [473, 851, 745, 620, 600, 721, 823, 895, 389, 1333],
                "Gig Apps": [281, 450, 387, 314, 379, 254, 662, 371, 210, 587],
                "Freelancers": [430, 642, 597, 421, 678, 456, 786, 611, 308, 936],
                "Covid": [306, 514, 561, 340, 391, 390, 526, 531, 249, 807],
                "AI in gig work": [554, 1004, 880, 717, 729, 725, 997, 1018, 474, 1477]
            }
        st.write("**How are HRM Practices related to the Discourse Topics?**")
    
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Melt the dataframe for Plotly
        df_melted = df.melt(id_vars=["HRM Practices"], 
                            var_name="Topic", 
                            value_name="Weight")
        
        # Create radar chart
        practice = st.selectbox("Select HRM Practice to Visualize:", df["HRM Practices"])
        
        # Filter data for selected practice
        filtered_df = df_melted[df_melted["HRM Practices"] == practice]
        
        fig = px.line_polar(
            filtered_df, 
            r="Weight", 
            theta="Topic",
            line_close=True,
            template="plotly_dark",
            # title=f"{practice} Relationship with Discourse Topics by Topic Weights"
        )
        
        fig.update_traces(fill='toself')
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, df_melted["Weight"].max() * 1.1]
                )),
            showlegend=False,
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
elif menu == "Impact Metrics Hub":
    st.title("Impact Metrics Hub")
    st.markdown("### Tracking HR performance metrics for departments managing gig workers—including job satisfaction, psychological safety, positive work environment, and inclusion climate—is essential for fostering transparency and upholding accountability in the gig economy.")
    st.markdown("---")
    
    def generate_hr_performance_data():
        hr_groups = ["Recruitment", "Onboarding", "Training", "Compensation", "Employee Relations", "Diversity & Inclusion"]
        months = [datetime.now().strftime("%B %Y")]
        
        data = []
        for group in hr_groups:
            data.append({
                "HR Group": group,
                "Performance Score": random.randint(70, 100),
                "Gig Worker's Job Satisfaction": random.randint(70, 100),   # measured via JSS scale
                "Gig Worker's Psychological Safety": random.randint(70, 100),        # measured through PsychSafety scale
                "Positive Work Environment for Gig Workers": random.randint(70, 100),  # measured through InterpersCitizBehav
                "Inclusion Climate for Gig Workers": random.randint(75,90),             # measured through Kossek's scale on inclusion
                "Month": months[0]
            })
        return pd.DataFrame(data)

    # Apply manual styling
    def colorize(val):
        if val > 90:
            color = 'green'
        elif val > 80:
            color = 'lightgreen'
        elif val > 70:
            color = 'yellow'
        else:
            color = 'white'
        return f'background-color: {color}'
    # Generate or load performance data
    performance_df = generate_hr_performance_data()
    
    # Generate or load performance data
    performance_df = generate_hr_performance_data()
    
    # Display leaderboard
    st.subheader("Current Month Leaderboard")
    
    # Sort by performance score
    leaderboard_df = performance_df.sort_values("Performance Score", ascending=False)
    leaderboard_df = leaderboard_df.reset_index(drop=True)
    leaderboard_df.index = leaderboard_df.index + 1  # Start ranking at 1
    
    # Apply manual styling
    styled_df = leaderboard_df.style.applymap(colorize, subset=["Performance Score"])
    
    # Display styled leaderboard
    st.dataframe(
        styled_df.format({
            "Performance Score": "{:.0f}", 
            "Employee Satisfaction": "{:.0f}", 
            "Process Efficiency": "{:.0f}"
        }),
        use_container_width=True
    )
    
    # Rest of your code remains the same...
    # Survey section
    st.markdown("---")
    st.subheader("Join the Performance Ratings Program")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Want your team to participate in next month's ratings?**
        
        Send this survey link to the gig workers in your team to collect their anonymous feedback:
        """)
        
        survey_link = "https://qualtricsxmqkspmg99k.qualtrics.com/jfe/form/SV_43eZXhMl5krog0m"
        st.code(survey_link, language="HTML")
        
        st.markdown("""
        The survey will ask gig workers to rate your HR department on the basis of:
        - Job Satisfaction
        - Psychological Safety
        - Positive Work Environment
        - Inclusion Climate
        """)
    st.subheader("📬 Got Any Questions?")
    st.write("Contact Us: vsingh@is.mpg.de")
    

elif menu == "HR Voices and Sentiments":
    st.title("HR Voices and Sentiments")
    st.subheader("Authentic stories and diverse perspectives from HR managers across the globe, sharing their real-world experiences in managing gig workers. It also highlights the innovative tools HR managers wish existed to better support their crucial work.")

    st.markdown("---")

    
    st.subheader("👥 Sentiments of HR Managers towards Gig Workers")
    sentiment_data = {
    "HRM Practice": ["Train.&Development", "Org.Culture", "Motivation", "Leadership", "Job Design", "HRM", "Comp&Benefits", "Health and Safety", "Selection", "D&I"],
    "Positive": [46, 39, 32, 47, 43, 44, 36, 36, 42, 24],
    "Negative": [6, 3, 9, 0, 7, 1, 6, 7, 5, 9],
    "Neutral": [44, 58, 56, 53, 49, 54, 55, 55, 53, 65],
    "Mixed": [4, 0, 3, 0, 1, 1, 3, 2, 0, 2]}
    # Convert to DataFrame
    df = pd.DataFrame(sentiment_data)
    
    # Calculate average sentiments
    avg_sentiments = df[["Positive", "Negative", "Neutral", "Mixed"]].mean().reset_index()
    avg_sentiments.columns = ["Sentiment", "Percentage"]
    
    # Create expandable sections for each sentiment
    sentiment_cols = st.columns(4)
    sentiment_info = {
        "Positive": {"color": "#2ecc71", "icon": "😊"},
        "Negative": {"color": "#e74c3c", "icon": "😞"},
        "Neutral": {"color": "#3498db", "icon": "😐"},
        "Mixed": {"color": "#9b59b6", "icon": "😕"}
    }
    
    # Initialize session state for expanded sentiment
    if "expanded_sentiment" not in st.session_state:
        st.session_state.expanded_sentiment = None
    
    # Display sentiment cards
    for i, (sentiment, info) in enumerate(sentiment_info.items()):
        with sentiment_cols[i]:
            percentage = avg_sentiments[avg_sentiments["Sentiment"] == sentiment]["Percentage"].values[0]
            st.markdown(
                f"""
                <div style='
                    padding: 15px;
                    border-radius: 8px;
                    background-color: {info["color"]}20;
                    border-left: 4px solid {info["color"]};
                    margin-bottom: 10px;
                    cursor: pointer;
                ' onclick='window.streamlitScript.setComponentValue("{sentiment}")'>
                    <h3>{info["icon"]} {sentiment}</h3>
                    <h2>{percentage:.1f}%</h2>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Show main visualization
    st.markdown("---")
    st.subheader("Sentiment Distribution Across Top 10 HRM Practices")
    
    # Melt data for visualization
    df_melted = df.melt(id_vars=["HRM Practice"], var_name="Sentiment", value_name="Percentage")
    
    # Create interactive bar chart
    fig = px.bar(df_melted, 
                 x="HRM Practice", 
                 y="Percentage",
                 color="Sentiment",
                 color_discrete_map={
                     "Positive": "#2ecc71",
                     "Negative": "#e74c3c",
                     "Neutral": "#3498db",
                     "Mixed": "#9b59b6"
                 },
                 barmode="group",
                 height=500)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Handle sentiment selection
    selected_sentiment = st.session_state.get("expanded_sentiment")
    if selected_sentiment:
        st.session_state.expanded_sentiment = None
        
        # Find HRM Practice with highest selected sentiment
        max_HRM_Practice = df.loc[df[selected_sentiment].idxmax()]
        
        # Display details
        st.markdown("---")
        st.subheader(f"HRM Practice with Highest {selected_sentiment} Sentiment")
        
        cols = st.columns([1, 3])
        with cols[0]:
            st.metric(label="HRM Practice", value=max_HRM_Practice["HRM Practice"])
            st.metric(label=f"{selected_sentiment} Score", 
                     value=f"{max_HRM_Practice[selected_sentiment]}%")
        
        with cols[1]:
            # Create a mini pie chart for this HRM Practice
            pie_data = max_HRM_Practice[["Positive", "Negative", "Neutral", "Mixed"]]
            pie_fig = px.pie(
                values=pie_data,
                names=pie_data.index,
                color=pie_data.index,
                color_discrete_map={
                    "Positive": "#2ecc71",
                    "Negative": "#e74c3c",
                    "Neutral": "#3498db",
                    "Mixed": "#9b59b6"
                },
                hole=0.4,
                height=200
            )
            pie_fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(pie_fig, use_container_width=True)
        
        # Show all sentiments for this HRM Practice
        st.markdown("### All Sentiments for This HRM Practice")
        st.dataframe(
            pd.DataFrame({
                "Sentiment": ["Positive", "Negative", "Neutral", "Mixed"],
                "Percentage": [
                    max_HRM_Practice["Positive"],
                    max_HRM_Practice["Negative"],
                    max_HRM_Practice["Neutral"],
                    max_HRM_Practice["Mixed"]
                ]
            }).style.background_gradient(cmap="Blues"),
            use_container_width=True
        )
        
        st.experimental_rerun()
    
    st.markdown("---")
    st.subheader("📖 Stories from HR Professionals")

    stories = load_stories()
    for _, row in stories.iterrows():
        st.write(f"**{row['role']}** ({row['name']}) ({row['timestamp']}):")
        st.info(row['story'])
        
    st.markdown("---")
    st.subheader("🛠️ Tool Requirements from HR Managers")
    st.write("**How to use:** Click on See Explanation to know more.")
    tools_data = {
            "🦾 AI-Integrated Tools": "AI-Integrated Tools for Gig Workers' Project and Performance Management",
            "🚕 Gig Apps": "Apps to track the automate attendance of gig workers",}    

    cols = st.columns(2)  # 2-column layout
    # for i, name in enumerate(names):
    for i, (tool, description) in enumerate(tools_data.items()):
        with cols[i % 2]:  # Alternate between columns
            st.markdown(
                f"""
                <div style='padding: 10px; border-radius: 5px; 
                background-color: #888f7a; margin: 5px 0;'>
                {tool}
                </div>
                """,
                unsafe_allow_html=True
            )
            with st.expander("See explanation"):
                st.write(description)
    st.write("For collaborations, contact: vsingh@is.mpg.de")
    
    st.markdown("---")
    st.subheader("📝 Share Your Story")

    with st.form("story_form"):
        name = st.text_input("Your Location")
        role = st.text_input("Your Role")
        story = st.text_area("What’s your experience managing gig workers?")
        submitted = st.form_submit_button("Submit Story")

    if submitted:
        submit_story_to_firebase(name, role, story)
        st.success("Thanks for sharing your story!")
    # with st.form("story_form"):
    #     name = st.text_input("Your Location")
    #     role = st.text_input("Your Role")
    #     story = st.text_area("What’s your experience managing gig workers?")
    #     submitted = st.form_submit_button("Submit Story")
    #     if submitted:
    #         save_story(name, role, story)
    #         st.success("Thanks for sharing your story!")

# # In your page routing:
if menu == "Transparency Tracker":
    hr_survey_page()
