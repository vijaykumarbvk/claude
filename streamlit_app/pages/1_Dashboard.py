import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
from utils import auth
from utils.dashboards import ROLE_RENDERERS

st.set_page_config(page_title="Dashboard | Venus Hospital", page_icon="🏥", layout="wide")
auth.require_login()

user = auth.current_user()

with st.sidebar:
    st.markdown(f"### 👤 {user['firstName']} {user['lastName']}")
    st.caption(user["role"].replace("_", " ").title())
    st.divider()
    if st.button("Log Out", use_container_width=True):
        auth.logout_user()
        st.switch_page("Home.py")

renderer = ROLE_RENDERERS.get(user["role"])
if renderer:
    renderer(user)
else:
    st.error(f"No dashboard configured for role: {user['role']}")
