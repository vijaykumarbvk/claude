"""
One render_xxx_dashboard(user) function per role — equivalent to the
React pages/dashboards/*.tsx components. Each is self-contained so
Dashboard.py can simply dispatch on user['role'].
"""
from datetime import datetime

import pandas as pd
import streamlit as st

from utils import api_client


def _status_badge(status: str) -> str:
    colors = {
        "SCHEDULED": "🔵", "CONFIRMED": "🟣", "IN_PROGRESS": "🟡",
        "COMPLETED": "🟢", "CANCELLED": "🔴", "NO_SHOW": "⚪",
    }
    return f"{colors.get(status, '⚪')} {status.replace('_', ' ').title()}"


# ------------------------------------------------------------------ #
# PATIENT
# ------------------------------------------------------------------ #
def render_patient_dashboard(user: dict):
    st.header(f"Welcome back, {user['firstName']}! 👋")

    profile_resp = api_client.get_patient_by_user_id(user["id"])
    patient = profile_resp.get("data") if profile_resp.get("success") else None

    col1, col2, col3, col4 = st.columns(4)
    appointments = []
    if patient:
        appt_resp = api_client.get_patient_appointments(patient["id"])
        appointments = appt_resp.get("data", []) or []

    upcoming = [a for a in appointments if a["status"] in ("SCHEDULED", "CONFIRMED")]
    completed = [a for a in appointments if a["status"] == "COMPLETED"]

    col1.metric("Upcoming Appointments", len(upcoming))
    col2.metric("Total Visits", len(completed))
    col3.metric("Blood Group", patient["bloodGroup"] if patient else "N/A")
    col4.metric("BMI", patient["bmi"] if patient and patient.get("bmi") else "N/A")

    st.divider()
    left, right = st.columns([2, 1])

    with left:
        st.subheader("📅 Upcoming Appointments")
        if upcoming:
            df = pd.DataFrame([{
                "Doctor": a["doctorName"] or f"#{a['doctorId']}",
                "Date/Time": a["appointmentDateTime"],
                "Type": a["appointmentType"],
                "Status": _status_badge(a["status"]),
            } for a in upcoming])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No upcoming appointments. Book one from the Appointments page.")
        st.page_link("pages/2_Appointments.py", label="Book a new appointment →", icon="📅")

    with right:
        st.subheader("🩺 Health Profile")
        if patient:
            st.write(f"**Age:** {patient.get('age', 'N/A')}")
            st.write(f"**Gender:** {patient.get('gender', 'N/A')}")
            st.write(f"**Height:** {patient.get('height', 'N/A')} cm")
            st.write(f"**Weight:** {patient.get('weight', 'N/A')} kg")
            if patient.get("allergies"):
                st.warning(f"**Allergies:** {patient['allergies']}")
        else:
            st.info("Complete your patient profile to see health insights here.")


# ------------------------------------------------------------------ #
# DOCTOR
# ------------------------------------------------------------------ #
def render_doctor_dashboard(user: dict):
    st.header(f"Good day, Dr. {user['lastName']}! 🩺")

    profile_resp = api_client.get_doctor_by_user_id(user["id"])
    doctor = profile_resp.get("data") if profile_resp.get("success") else None

    appointments = []
    if doctor:
        appt_resp = api_client.get_doctor_appointments(doctor["id"])
        appointments = appt_resp.get("data", []) or []

    today_str = datetime.now().date().isoformat()
    today_appts = [a for a in appointments if a["appointmentDateTime"].startswith(today_str)]
    completed_today = [a for a in today_appts if a["status"] == "COMPLETED"]
    pending_today = [a for a in today_appts if a["status"] in ("SCHEDULED", "CONFIRMED")]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Today's Appointments", len(today_appts))
    col2.metric("Completed Today", len(completed_today))
    col3.metric("Pending Today", len(pending_today))
    col4.metric("Total Patients", len({a["patientId"] for a in appointments}))

    st.divider()
    st.subheader("Today's Schedule")

    if not today_appts:
        st.info("No appointments scheduled for today.")
        return

    for appt in sorted(today_appts, key=lambda a: a["appointmentDateTime"]):
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 2])
            patient_label = appt["patientName"] or f"Patient #{appt['patientId']}"
            c1.markdown(f"**{patient_label}**")
            c1.caption(appt.get("chiefComplaint") or "No chief complaint noted")
            c2.write(_status_badge(appt["status"]))
            c2.caption(appt["appointmentDateTime"])

            next_status = {
                "SCHEDULED": "CONFIRMED", "CONFIRMED": "IN_PROGRESS", "IN_PROGRESS": "COMPLETED",
            }.get(appt["status"])

            if next_status and c3.button(f"Mark {next_status.replace('_', ' ').title()}", key=f"appt-{appt['id']}"):
                result = api_client.update_appointment_status(appt["id"], next_status)
                if result.get("success"):
                    st.rerun()
                else:
                    st.error(result.get("message"))


# ------------------------------------------------------------------ #
# ASSISTANT DOCTOR
# ------------------------------------------------------------------ #
def render_assistant_doctor_dashboard(user: dict):
    st.header(f"Assistant Dashboard — {user['firstName']} {user['lastName']} 🧑‍⚕️")

    doctors_resp = api_client.get_active_doctors()
    doctors = (doctors_resp.get("data") or [])[:3]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Today's Appointments", 12)
    col2.metric("Completed Tasks", 8)
    col3.metric("Pending Reports", 4)
    col4.metric("Patients Assisted", 35)

    st.divider()
    left, right = st.columns([2, 1])

    with left:
        st.subheader("📋 Today's Tasks")
        tasks = [
            ("Prepare patient reports", "For morning rounds", "In Progress", "🟡"),
            ("Assist with consultations", "Cardiology — 5 patients", "Pending", "🔵"),
            ("Review lab test results", "10 reports to review", "Pending", "🔵"),
            ("Update patient vitals", "Ward A & B, completed 8:30 AM", "Completed", "🟢"),
        ]
        for title, detail, status, icon in tasks:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"**{title}**")
                c1.caption(detail)
                c2.write(f"{icon} {status}")

    with right:
        st.subheader("👥 Assigned Doctors")
        for doc in doctors:
            st.write(f"**{doc.get('doctorName', 'Doctor')}** — {doc.get('specialization', '')}")
        st.divider()
        st.subheader("🗓️ Today's Schedule")
        st.write("**Morning Rounds** — 8:00–10:00 AM")
        st.write("**OPD Assistance** — 10:00 AM–2:00 PM")
        st.write("**Lab Review** — 2:00–4:00 PM")
        st.write("**Evening Rounds** — 4:00–6:00 PM")


# ------------------------------------------------------------------ #
# SURGEON
# ------------------------------------------------------------------ #
def render_surgeon_dashboard(user: dict):
    st.header(f"Surgeon Dashboard — Dr. {user['firstName']} {user['lastName']} 🔪")

    surgeries = [
        {"patient": "Rajesh Kumar", "type": "Appendectomy", "time": "09:00", "ot": "OT-1",
         "priority": "ROUTINE", "team": ["Dr. Sharma", "Nurse Alice", "Anesthetist John"]},
        {"patient": "Priya Desai", "type": "Laparoscopic Cholecystectomy", "time": "11:30", "ot": "OT-2",
         "priority": "URGENT", "team": ["Dr. Patel", "Nurse Mary", "Anesthetist David"]},
        {"patient": "Amit Singh", "type": "Hernia Repair", "time": "14:00", "ot": "OT-1",
         "priority": "ROUTINE", "team": ["Dr. Kumar", "Nurse Sarah"]},
    ]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Today's Surgeries", len(surgeries))
    col2.metric("Completed", 0)
    col3.metric("Upcoming", len(surgeries))
    col4.metric("Emergencies", sum(1 for s in surgeries if s["priority"] == "EMERGENCY"))

    st.divider()
    left, right = st.columns([2, 1])

    with left:
        st.subheader("🗓️ Today's Surgery Schedule")
        for s in surgeries:
            border_icon = "🔴" if s["priority"] == "EMERGENCY" else "🟠" if s["priority"] == "URGENT" else "🔵"
            with st.container(border=True):
                st.markdown(f"### {border_icon} {s['type']}")
                st.write(f"**Patient:** {s['patient']}")
                st.write(f"**Time:** {s['time']} · **OT:** {s['ot']} · **Priority:** {s['priority']}")
                st.write(f"**Team:** {', '.join(s['team'])}")
                c1, c2 = st.columns(2)
                c1.button("View Details", key=f"details-{s['patient']}")
                c2.button("Pre-Op Checklist", key=f"checklist-{s['patient']}")

    with right:
        st.subheader("🏥 OT Availability")
        ot_status = {"OT-1": "Available", "OT-2": "In Use", "OT-3": "Available", "OT-4": "Maintenance"}
        for ot, status in ot_status.items():
            icon = {"Available": "🟢", "In Use": "🔴", "Maintenance": "🟡"}[status]
            st.write(f"{icon} **{ot}** — {status}")

        st.divider()
        st.subheader("📊 This Month")
        st.metric("Total Surgeries", 47)
        st.metric("Success Rate", "98.5%")
        st.metric("Avg Duration", "85 min")


# ------------------------------------------------------------------ #
# ADMIN
# ------------------------------------------------------------------ #
def render_admin_dashboard(user: dict):
    st.header("Admin Dashboard 🏥")
    st.caption("Venus Multispecialty Hospital Management")

    users_resp = api_client.get_active_users()
    doctors_resp = api_client.get_active_doctors()
    patients_resp = api_client.get_active_patients()

    users = users_resp.get("data", []) or []
    doctors = doctors_resp.get("data", []) or []
    patients = patients_resp.get("data", []) or []

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Users", len(users))
    col2.metric("Total Doctors", len(doctors))
    col3.metric("Total Patients", len(patients))
    col4.metric("Active Doctors", sum(1 for d in doctors if d.get("active")))

    st.divider()
    left, right = st.columns([2, 1])

    with left:
        st.subheader("👨‍⚕️ Active Doctors")
        if doctors:
            df = pd.DataFrame([{
                "Name": d.get("doctorName"),
                "Specialization": d.get("specialization"),
                "Department": d.get("department"),
                "Experience": f"{d.get('experienceYears', 0)} yrs",
            } for d in doctors])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No doctors registered yet.")

        st.subheader("🏬 Department Distribution")
        if doctors:
            dept_counts = pd.Series([d.get("department", "Unknown") for d in doctors]).value_counts()
            st.bar_chart(dept_counts)

    with right:
        st.subheader("⚙️ System Status")
        for svc in ["User Service", "Appointment Service", "Doctor Service", "Patient Service", "API Gateway"]:
            st.write(f"🟢 **{svc}** — Active")

        st.divider()
        st.subheader("🚀 Quick Actions")
        st.page_link("pages/3_Directory.py", label="Manage Doctors & Patients", icon="👥")
        st.page_link("pages/2_Appointments.py", label="View All Appointments", icon="📅")


ROLE_RENDERERS = {
    "PATIENT": render_patient_dashboard,
    "DOCTOR": render_doctor_dashboard,
    "ASSISTANT_DOCTOR": render_assistant_doctor_dashboard,
    "SURGEON": render_surgeon_dashboard,
    "ADMIN": render_admin_dashboard,
}
