# frontend/student_dashboard.py
import streamlit as st
import requests
from pathlib import Path
import streamlit as st

if "role" not in st.session_state or st.session_state.get("role") != "student":
    st.error("Access denied. Only students can view this page.")
    st.stop()


# ---------------- Configuration ----------------
# Update this if your backend endpoint is different
BACKEND_EVALUATE_URL = "http://127.0.0.1:8000/evaluate_resume/"  # <- make sure this matches your FastAPI route

# Local sample JDs folder (optional)
SAMPLE_JDS_DIR = Path(__file__).parent / "sample_jds"

# ---------------- Helper functions ----------------
def load_sample_jds():
    """Return a dict {filename: content} of text files in sample_jds folder."""
    jds = {}
    if SAMPLE_JDS_DIR.exists() and SAMPLE_JDS_DIR.is_dir():
        for p in SAMPLE_JDS_DIR.glob("*"):
            if p.suffix.lower() in {".txt", ".md", ".json", ".jobdesc"}:
                try:
                    jds[p.name] = p.read_text(encoding="utf-8")
                except Exception:
                    jds[p.name] = ""
            elif p.suffix.lower() in {".pdf", ".docx"}:
                # we won't parse PDFs here; just show filename
                jds[p.name] = f"[binary file: {p.name}]"
    return jds

def pretty_missing_skills(ms):
    if ms is None:
        return "None"
    if isinstance(ms, list):
        return ", ".join(ms) if ms else "None"
    # If server returned comma-separated string
    return str(ms)

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Student Resume Upload", layout="centered")
st.title("Student Resume — Upload & Get Feedback")

# Student inputs
student_name = st.text_input("Your name", "")
job_role = st.text_input("Job role you are applying for", "")
skills = st.text_input("Skills (comma-separated)", "")

# Job description selection: sample or paste
st.subheader("Job Description (JD)")
sample_jds = load_sample_jds()
jd_option = st.radio("Choose JD source", ("Paste JD", "Use sample JD"))

if jd_option == "Paste JD":
    jd_text = st.text_area("Paste the full job description here", height=200)
else:
    if sample_jds:
        selected_jd = st.selectbox("Select a sample JD", ["-- choose --"] + list(sample_jds.keys()))
        jd_text = sample_jds[selected_jd] if selected_jd and selected_jd != "-- choose --" else ""
        st.text_area("Selected JD (editable)", value=jd_text, height=200, key="selected_jd_text")
        # pick up any edits
        jd_text = st.session_state.get("selected_jd_text", jd_text)
    else:
        st.info("No sample JDs found in frontend/sample_jds. Switch to 'Paste JD' or add files there.")
        jd_text = st.text_area("Paste the full job description here", height=200)

# Resume file uploader
st.subheader("Upload your resume (PDF or DOCX)")
uploaded_file = st.file_uploader("Choose a resume file", type=["pdf", "docx"])

# Evaluate button
if st.button("Evaluate Resume"):
    # Basic validations
    if not student_name.strip():
        st.error("Please enter your name.")
    elif not job_role.strip():
        st.error("Please enter the job role.")
    elif not jd_text.strip():
        st.error("Please provide/paste the job description.")
    elif not uploaded_file:
        st.error("Please upload your resume (PDF or DOCX).")
    else:
        # Read uploaded file bytes
        try:
            file_bytes = uploaded_file.read()
        except Exception as e:
            st.error(f"Could not read uploaded file: {e}")
            file_bytes = None

        if file_bytes:
            # Build files and data for requests
            # Backend expects: resume file + form fields (student_name, job_role, jd_text, skills)
            files = {
                "file": (uploaded_file.name, file_bytes, uploaded_file.type or "application/octet-stream")
            }
            data = {
                "student_name": student_name,
                "job_role": job_role,
                "jd_text": jd_text,
                "skills": skills
            }

            # Call backend
            with st.spinner("Evaluating resume — contacting backend..."):
                try:
                    resp = requests.post(BACKEND_EVALUATE_URL, data=data, files=files, timeout=120)
                except requests.exceptions.RequestException as e:
                    st.error(f"Request failed: {e}")
                    resp = None

            if resp is None:
                pass
            elif resp.status_code != 200:
                st.error(f"Backend returned error (status {resp.status_code}): {resp.text}")
            else:
                try:
                    result = resp.json()
                except Exception:
                    st.error("Backend returned non-JSON response.")
                    result = {}

                # Robustly extract fields (handle different backend key names)
                score = result.get("relevance_score") or result.get("score") or result.get("relevance") or None
                verdict = result.get("verdict") or result.get("fit") or None
                missing_skills = result.get("missing_skills") or result.get("missing") or None
                feedback = result.get("feedback") or result.get("gpt_feedback") or None

                # Display results
                st.subheader("Evaluation Result")
                if score is not None:
                    try:
                        st.metric("Relevance Score", f"{float(score):.2f}/100")
                    except Exception:
                        st.metric("Relevance Score", str(score))
                else:
                    st.write("Relevance Score: N/A")

                st.write("Verdict:", verdict or "N/A")
                st.write("Missing Skills:", pretty_missing_skills(missing_skills))
                if feedback:
                    st.markdown("**Personalized feedback (LLM):**")
                    st.info(feedback)
                else:
                    st.info("No feedback returned by backend.")
