# frontend/admin_dashboard.py
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from collections import Counter
import streamlit as st

if "role" not in st.session_state or st.session_state.get("role") != "hr":
    st.error("Access denied. Only HR can view this page.")
    st.stop()


st.title("Placement Team Dashboard")

# --- Helper to highlight JD skills inside resume ---
def highlight_skills(text, jd_skills):
    for skill in jd_skills:
        text = text.replace(skill, f"**{skill}**")  # bold match
    return text

# Fetch all resume evaluations
response = requests.get("http://127.0.0.1:8000/get_all_evaluations")
if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)
    
    # Filters
    job_filter = st.selectbox("Filter by Job Role", ["All"] + df['job_role'].unique().tolist())
    verdict_filter = st.selectbox("Filter by Verdict", ["All", "High", "Medium", "Low"])
    
    filtered_df = df
    if job_filter != "All":
        filtered_df = filtered_df[filtered_df['job_role']==job_filter]
    if verdict_filter != "All":
        filtered_df = filtered_df[filtered_df['verdict']==verdict_filter]

    # Show table
    st.dataframe(filtered_df)

    # --- Highlight JD skills inside resume text ---
    if not filtered_df.empty:
        jd_skills = st.text_input("Enter JD skills (comma separated)", "Python, SQL, ML")
        if jd_skills:
            jd_skills = [s.strip() for s in jd_skills.split(",")]
            st.subheader("Highlighted Resume Sample")
            resume_text = filtered_df.iloc[0]["feedback"]  # or actual resume_text if stored
            st.markdown(highlight_skills(resume_text, jd_skills))

    # Download CSV
    csv = filtered_df.to_csv(index=False)
    st.download_button("Download CSV", csv, file_name="resume_report.csv", mime="text/csv")

    # --- Missing skills visualization ---
    all_missing_skills = []
    for ms in filtered_df['missing_skills']:
        all_missing_skills += ms.split(", ")
    if all_missing_skills:
        counter = Counter(all_missing_skills)
        top_skills = pd.DataFrame(counter.items(), columns=["Skill", "Count"])
        top_skills = top_skills.sort_values(by="Count", ascending=False).head(10)

        fig = px.bar(top_skills, x="Skill", y="Count", title="Top Missing Skills")
        st.plotly_chart(fig)

else:
    st.error("Error fetching data")




# --- Missing skills visualization ---
all_missing_skills = []
for ms in filtered_df['missing_skills']:
    all_missing_skills += ms.split(", ")
if all_missing_skills:
    counter = Counter(all_missing_skills)
    top_skills = pd.DataFrame(counter.items(), columns=["Skill", "Count"])
    top_skills = top_skills.sort_values(by="Count", ascending=False).head(10)

    fig = px.bar(top_skills, x="Skill", y="Count", title="Top Missing Skills")
    st.plotly_chart(fig)
