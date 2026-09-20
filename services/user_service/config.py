import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:root@localhost:3306/venus_user_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVICE_NAME = "user-service"
    SERVICE_PORT = int(os.environ.get("SERVICE_PORT", 8081))
