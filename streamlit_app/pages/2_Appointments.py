import sys
from datetime import date, datetime, time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
import streamlit as st
from utils import api_client, auth

st.set_page_config(page_title="Appointments | Venus Hospital", page_icon="📅", layout="wide")
auth.require_login()
user = auth.current_user()

st.title("📅 Appointments")

with st.sidebar:
    st.markdown(f"### 👤 {user['firstName']} {user['lastName']}")
    st.caption(user["role"].replace("_", " ").title())
    if st.button("Log Out", use_container_width=True):
        auth.logout_user()
        st.switch_page("Home.py")

if user["role"] == "PATIENT":
    profile_resp = api_client.get_patient_by_user_id(user["id"])
    patient = profile_resp.get("data") if profile_resp.get("success") else None

    if not patient:
        st.warning("Complete your patient profile before booking an appointment.")
        st.stop()

    tab_book, tab_mine = st.tabs(["Book New Appointment", "My Appointments"])

    with tab_book:
        doctors_resp = api_client.get_active_doctors()
        doctors = doctors_resp.get("data", []) or []

        if not doctors:
            st.info("No doctors are available right now. Please check back later.")
        else:
            with st.form("book_appointment"):
                doctor_options = {f"{d['doctorName']} — {d['specialization']}": d["id"] for d in doctors}
                doctor_label = st.selectbox("Choose a doctor", list(doctor_options.keys()))

                col1, col2 = st.columns(2)
                appt_date = col1.date_input("Date", min_value=date.today())
                appt_time = col2.time_input("Time", value=time(9, 0))

                consultation_type = st.radio("Consultation type", ["IN_PERSON", "TELEMEDICINE"], horizontal=True)
                appointment_type = st.selectbox("Appointment type", ["CONSULTATION", "FOLLOW_UP", "EMERGENCY"])
                chief_complaint = st.text_input("Chief complaint")
                symptoms = st.text_area("Symptoms (optional)")

                submitted = st.form_submit_button("Book Appointment", type="primary")

                if submitted:
                    appt_datetime = datetime.combine(appt_date, appt_time)
                    payload = {
                        "patientId": patient["id"],
                        "doctorId": doctor_options[doctor_label],
                        "appointmentDateTime": appt_datetime.isoformat(),
                        "chiefComplaint": chief_complaint,
                        "symptoms": symptoms,
                        "consultationType": consultation_type,
                        "appointmentType": appointment_type,
                        "durationMinutes": 30,
                    }
                    result = api_client.create_appointment(payload)
                    if result.get("success"):
                        st.success("Appointment booked successfully!")
                        st.rerun()
                    else:
                        st.error(result.get("message", "Booking failed"))

    with tab_mine:
        appt_resp = api_client.get_patient_appointments(patient["id"])
        appointments = appt_resp.get("data", []) or []
        if appointments:
            df = pd.DataFrame([{
                "Doctor": a["doctorName"] or f"#{a['doctorId']}",
                "Date/Time": a["appointmentDateTime"],
                "Type": a["appointmentType"],
                "Status": a["status"],
            } for a in appointments])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("You haven't booked any appointments yet.")

elif user["role"] in ("DOCTOR", "ASSISTANT_DOCTOR", "SURGEON"):
    doctor_resp = api_client.get_doctor_by_user_id(user["id"])
    doctor = doctor_resp.get("data") if doctor_resp.get("success") else None

    if not doctor:
        st.info("No doctor profile linked to this account yet.")
    else:
        appt_resp = api_client.get_doctor_appointments(doctor["id"])
        appointments = appt_resp.get("data", []) or []

        if not appointments:
            st.info("No appointments found.")
        else:
            for appt in sorted(appointments, key=lambda a: a["appointmentDateTime"]):
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 2])
                    patient_label = appt["patientName"] or f"Patient #{appt['patientId']}"
                    c1.markdown(f"**{patient_label}**")
                    c1.caption(appt.get("chiefComplaint", ""))
                    c2.write(appt["appointmentDateTime"])
                    c2.caption(appt["status"])

                    new_status = c3.selectbox(
                        "Update status", ["SCHEDULED", "CONFIRMED", "IN_PROGRESS", "COMPLETED", "CANCELLED", "NO_SHOW"],
                        index=["SCHEDULED", "CONFIRMED", "IN_PROGRESS", "COMPLETED", "CANCELLED", "NO_SHOW"].index(appt["status"]),
                        key=f"status-{appt['id']}",
                        label_visibility="collapsed",
                    )
                    if new_status != appt["status"] and c3.button("Update", key=f"update-{appt['id']}"):
                        result = api_client.update_appointment_status(appt["id"], new_status)
                        if result.get("success"):
                            st.rerun()
                        else:
                            st.error(result.get("message"))

else:  # ADMIN
    st.info("Admin appointment oversight — pick a doctor from the Directory page to view their schedule.")
