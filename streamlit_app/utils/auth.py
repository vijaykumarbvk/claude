"""
Session-state based auth helpers, equivalent to the React AuthContext.
Streamlit has no client-side routing guard, so every protected page calls
require_login() / require_role() at the top of the script.
"""
import streamlit as st


def is_authenticated() -> bool:
    return bool(st.session_state.get("token")) and bool(st.session_state.get("user"))


def current_user() -> dict | None:
    return st.session_state.get("user")


def login_user(token: str, refresh_token: str, user: dict):
    st.session_state["token"] = token
    st.session_state["refresh_token"] = refresh_token
    st.session_state["user"] = user


def logout_user():
    for key in ("token", "refresh_token", "user"):
        st.session_state.pop(key, None)


def require_login():
    if not is_authenticated():
        st.warning("Please sign in to continue.")
        st.page_link("Home.py", label="Go to Login", icon="🔐")
        st.stop()


def require_role(*allowed_roles: str):
    require_login()
    user = current_user()
    if user["role"] not in allowed_roles:
        st.error("You don't have permission to view this page.")
        st.stop()
