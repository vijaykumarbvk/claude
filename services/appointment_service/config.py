import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:root@localhost:3306/venus_appointment_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVICE_NAME = "appointment-service"
    SERVICE_PORT = int(os.environ.get("SERVICE_PORT", 8082))
    MAX_APPOINTMENTS_PER_DOCTOR_PER_DAY = 20
    CONFLICT_WINDOW_MINUTES = 30
