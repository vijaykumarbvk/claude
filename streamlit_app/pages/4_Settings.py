import sys
from datetime import date
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
from utils import api_client, auth

st.set_page_config(page_title="Settings | Venus Hospital", page_icon="⚙️", layout="wide")
auth.require_login()
user = auth.current_user()

st.title("⚙️ Settings")

with st.sidebar:
    st.markdown(f"### 👤 {user['firstName']} {user['lastName']}")
    st.caption(user["role"].replace("_", " ").title())
    if st.button("Log Out", use_container_width=True):
        auth.logout_user()
        st.switch_page("Home.py")

tab_profile, tab_clinical = st.tabs(["👤 Account", "🩺 Clinical Profile"])

with tab_profile:
    st.write(f"**Username:** {user['username']}")
    st.write(f"**Email:** {user['email']}")
    st.write(f"**Phone:** {user.get('phoneNumber', 'N/A')}")
    st.write(f"**Role:** {user['role'].replace('_', ' ').title()}")

with tab_clinical:
    if user["role"] == "PATIENT":
        existing = api_client.get_patient_by_user_id(user["id"])
        if existing.get("success"):
            st.success("Your patient profile is already set up. Contact admin to update sensitive fields.")
            st.json(existing["data"])
        else:
            st.info("Complete your patient profile so doctors have your health context.")
            with st.form("patient_profile_form"):
                col1, col2 = st.columns(2)
                dob = col1.date_input("Date of birth", max_value=date.today())
                gender = col2.selectbox("Gender", ["Male", "Female", "Other"])
                blood_group = st.selectbox("Blood group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                col3, col4 = st.columns(2)
                height = col3.number_input("Height (cm)", min_value=0.0, step=0.5)
                weight = col4.number_input("Weight (kg)", min_value=0.0, step=0.5)
                allergies = st.text_area("Allergies (optional)")
                emergency_name = st.text_input("Emergency contact name")
                emergency_phone = st.text_input("Emergency contact phone")

                submitted = st.form_submit_button("Save Profile", type="primary")
                if submitted:
                    payload = {
                        "userId": user["id"], "dateOfBirth": dob.isoformat(), "gender": gender,
                        "bloodGroup": blood_group, "height": height, "weight": weight,
                        "allergies": allergies, "emergencyContactName": emergency_name,
                        "emergencyContactPhone": emergency_phone,
                    }
                    result = api_client.create_patient(payload)
                    if result.get("success"):
                        st.success("Profile saved!")
                        st.rerun()
                    else:
                        st.error(result.get("message"))

    elif user["role"] in ("DOCTOR", "ASSISTANT_DOCTOR", "SURGEON"):
        existing = api_client.get_doctor_by_user_id(user["id"])
        if existing.get("success"):
            st.success("Your doctor profile is already set up.")
            st.json(existing["data"])
        else:
            st.info("Complete your professional profile.")
            with st.form("doctor_profile_form"):
                specialization = st.text_input("Specialization")
                license_number = st.text_input("License number")
                qualification = st.text_input("Qualification")
                col1, col2 = st.columns(2)
                experience = col1.number_input("Experience (years)", min_value=0, step=1)
                department = col2.text_input("Department")
                fee = st.number_input("Consultation fee (₹)", min_value=0.0, step=50.0)
                telemedicine = st.checkbox("Available for telemedicine")

                submitted = st.form_submit_button("Save Profile", type="primary")
                if submitted:
                    payload = {
                        "userId": user["id"], "specialization": specialization,
                        "licenseNumber": license_number, "qualification": qualification,
                        "experienceYears": experience, "department": department,
                        "consultationFee": fee, "availableForTelemedicine": telemedicine,
                        "workingDays": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"],
                        "availableFrom": "09:00:00", "availableTo": "17:00:00",
                    }
                    result = api_client.create_doctor(payload)
                    if result.get("success"):
                        st.success("Profile saved!")
                        st.rerun()
                    else:
                        st.error(result.get("message"))
    else:
        st.info("No clinical profile needed for this role.")
