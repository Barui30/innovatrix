import streamlit as st
import requests

st.title("Automated Resume Relevance Check System")

st.sidebar.header("Student Portal")
student_name = st.sidebar.text_input("Your Name")
job_role = st.sidebar.text_input("Job Role")
skills = st.sidebar.text_input("Your Skills (comma-separated)")
jd_text = st.text_area("Paste Job Description Here")
resume_file = st.file_uploader("Upload Resume", type=["pdf","docx"])

if st.button("Evaluate Resume"):
    if resume_file and student_name and job_role and skills and jd_text:
        files = {"resume": (resume_file.name, resume_file.getvalue())}
        data = {
            "student_name": student_name,
            "job_role": job_role,
            "jd_text": jd_text,
            "skills": skills
        }
        response = requests.post("http://127.0.0.1:8000/evaluate_resume/", data=data, files=files)
        if response.status_code == 200:
            result = response.json()
            st.success(f"Relevance Score: {result['score']:.2f}")
            st.info(f"Verdict: {result['verdict']}")
            st.warning(f"Missing Skills: {', '.join(result['missing_skills'])}")
            st.text(f"Feedback: {result['feedback']}")
        else:
            st.error("Error evaluating resume.")
    else:
        st.error("Please fill all fields and upload resume.")
