# frontend/login.py
import streamlit as st

# ----------------- Hardcoded users for demo -----------------
USERS = {
    "alice": {"password": "student123", "role": "student"},
    "bob": {"password": "hr123", "role": "hr"}
}

st.set_page_config(page_title="Login Page", layout="centered")
st.title("Login to Placement System")

# Input fields
username = st.text_input("Username")
password = st.text_input("Password", type="password")

# Initialize session_state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "role" not in st.session_state:
    st.session_state["role"] = None

# Login button
if st.button("Login"):
    username_clean = username.strip().lower()  # strip spaces + lowercase
    password_clean = password.strip()

    # Check credentials
    user = USERS.get(username_clean)
    if user and user["password"] == password_clean:
        st.success(f"Welcome {username_clean}! Role: {user['role']}")
        st.session_state["logged_in"] = True
        st.session_state["role"] = user["role"]
        st.session_state["username"] = username_clean
    else:
        st.error("Invalid username or password")

# ----------------- Redirect based on role -----------------
if st.session_state["logged_in"]:
    if st.session_state["role"] == "student":
        import student_dashboard
    elif st.session_state["role"] == "hr":
        import admin_dashboard
