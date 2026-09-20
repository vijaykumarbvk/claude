import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
import streamlit as st
from utils import api_client, auth

st.set_page_config(page_title="Directory | Venus Hospital", page_icon="👥", layout="wide")
auth.require_login()
user = auth.current_user()

st.title("👥 Directory")

with st.sidebar:
    st.markdown(f"### 👤 {user['firstName']} {user['lastName']}")
    st.caption(user["role"].replace("_", " ").title())
    if st.button("Log Out", use_container_width=True):
        auth.logout_user()
        st.switch_page("Home.py")

tab_doctors, tab_patients = st.tabs(["🩺 Doctors", "🧑‍🤝‍🧑 Patients"])

with tab_doctors:
    doctors_resp = api_client.get_active_doctors()
    doctors = doctors_resp.get("data", []) or []

    specializations = sorted({d.get("specialization") for d in doctors if d.get("specialization")})
    chosen = st.multiselect("Filter by specialization", specializations)
    filtered = [d for d in doctors if not chosen or d.get("specialization") in chosen]

    if filtered:
        df = pd.DataFrame([{
            "Name": d.get("doctorName"),
            "Specialization": d.get("specialization"),
            "Department": d.get("department"),
            "Experience (yrs)": d.get("experienceYears"),
            "Fee": d.get("consultationFee"),
            "Telemedicine": "Yes" if d.get("availableForTelemedicine") else "No",
        } for d in filtered])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No doctors match this filter.")

with tab_patients:
    if user["role"] not in ("ADMIN", "DOCTOR", "ASSISTANT_DOCTOR", "SURGEON"):
        st.warning("You don't have permission to view the patient directory.")
    else:
        patients_resp = api_client.get_active_patients()
        patients = patients_resp.get("data", []) or []

        if patients:
            df = pd.DataFrame([{
                "Name": p.get("patientName"),
                "Age": p.get("age"),
                "Gender": p.get("gender"),
                "Blood Group": p.get("bloodGroup"),
                "City": p.get("city"),
            } for p in patients])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No patients registered yet.")
