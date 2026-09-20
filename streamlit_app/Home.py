import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

import streamlit as st
from utils import api_client, auth

st.set_page_config(
    page_title="Venus Multispecialty Hospital",
    page_icon="🏥",
    layout="wide",
)

# ------------------------------------------------------------------ #
# Simple CSS polish (Streamlit-friendly, avoids fighting the framework)
# ------------------------------------------------------------------ #
st.markdown(
    """
    <style>
    .venus-hero {
        background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
    }
    .venus-hero h1 { margin-bottom: 0.25rem; }
    .venus-card {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.25rem;
        background: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_hero():
    st.markdown(
        """
        <div class="venus-hero">
            <h1>🏥 Venus Multispecialty Hospital</h1>
            <p style="font-size:1.1rem;opacity:0.9;">
                Your health, our priority — expert care across 25+ specialties, available 24/7.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_form():
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
                return
            with st.spinner("Signing in..."):
                response = api_client.login(username, password)

            if response.get("success"):
                data = response["data"]
                auth.login_user(data["token"], data["refreshToken"], data["user"])
                st.success(f"Welcome back, {data['user']['firstName']}!")
                st.switch_page("pages/1_Dashboard.py")
            else:
                st.error(response.get("message", "Login failed"))


def render_register_form():
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        first_name = col1.text_input("First Name")
        last_name = col2.text_input("Last Name")
        username = st.text_input("Username", key="reg_username")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        role = st.selectbox(
            "Register as",
            ["PATIENT", "DOCTOR", "ASSISTANT_DOCTOR", "SURGEON"],
            format_func=lambda r: r.replace("_", " ").title(),
        )
        col3, col4 = st.columns(2)
        password = col3.text_input("Password", type="password")
        confirm_password = col4.text_input("Confirm Password", type="password")

        submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

        if submitted:
            if password != confirm_password:
                st.error("Passwords do not match.")
                return
            if len(password) < 8:
                st.error("Password must be at least 8 characters.")
                return

            payload = {
                "firstName": first_name, "lastName": last_name, "username": username,
                "email": email, "phoneNumber": phone, "role": role, "password": password,
            }
            with st.spinner("Creating your account..."):
                response = api_client.register(payload)

            if response.get("success"):
                st.success("Account created! Please sign in from the Login tab.")
            else:
                st.error(response.get("message", "Registration failed"))


render_hero()

if auth.is_authenticated():
    user = auth.current_user()
    st.info(f"You're already signed in as **{user['firstName']} {user['lastName']}** ({user['role']}).")
    col1, col2 = st.columns(2)
    if col1.button("Go to Dashboard", type="primary", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")
    if col2.button("Log Out", use_container_width=True):
        auth.logout_user()
        st.rerun()
else:
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Why Venus Hospital?")
        st.markdown(
            """
            - 🩺 **500+ expert doctors** across every major specialty
            - 📅 **Easy appointment booking** with real-time availability
            - 🔒 **Secure medical records**, encrypted end-to-end
            - 🚑 **24/7 emergency care**
            - 💻 **Telemedicine** consultations from anywhere
            """
        )

    with col_right:
        st.markdown('<div class="venus-card">', unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Register"])
        with tab_login:
            render_login_form()
        with tab_register:
            render_register_form()
        st.markdown("</div>", unsafe_allow_html=True)
