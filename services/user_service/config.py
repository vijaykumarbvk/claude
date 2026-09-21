# import os


# class Config:
#     SQLALCHEMY_DATABASE_URI = os.environ.get(
#         "DATABASE_URL",
#         "mysql+pymysql://root:root@localhost:3306/venus_user_db",
#     )
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     SERVICE_NAME = "user-service"
#     SERVICE_PORT = int(os.environ.get("SERVICE_PORT", 8081))

import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key')
    
    DB_HOST = os.getenv("DB_HOST", "mysql-service")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "hospital_db")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
