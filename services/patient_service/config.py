import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:root@localhost:3306/venus_patient_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVICE_NAME = "patient-service"
    SERVICE_PORT = int(os.environ.get("SERVICE_PORT", 8084))
    USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://localhost:8081")
