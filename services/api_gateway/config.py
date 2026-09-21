# import os


# class Config:
#     SERVICE_NAME = "api-gateway"
#     SERVICE_PORT = int(os.environ.get("SERVICE_PORT", 8080))

#     # Route prefix -> downstream base URL (equivalent to Spring Cloud Gateway routes)
#     ROUTES = {
#         "/api/users": os.environ.get("USER_SERVICE_URL", "http://localhost:8081"),
#         "/api/appointments": os.environ.get("APPOINTMENT_SERVICE_URL", "http://localhost:8082"),
#         "/api/doctors": os.environ.get("DOCTOR_SERVICE_URL", "http://localhost:8083"),
#         "/api/patients": os.environ.get("PATIENT_SERVICE_URL", "http://localhost:8084"),
#     }

#     PUBLIC_PATHS = {
#         "/api/users/register",
#         "/api/users/login",
#         "/actuator/health",
#     }

#     REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
#     RATE_LIMIT = os.environ.get("RATE_LIMIT", "20 per 10 seconds")

import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key')
    
    # Microservice Endpoint URLs
    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:5001")
    DOCTOR_SERVICE_URL = os.getenv("DOCTOR_SERVICE_URL", "http://doctor-service:5002")
    PATIENT_SERVICE_URL = os.getenv("PATIENT_SERVICE_URL", "http://patient-service:5003")
    APPOINTMENT_SERVICE_URL = os.getenv("APPOINTMENT_SERVICE_URL", "http://appointment-service:5004")

    # Redis Caching Settings
    REDIS_HOST = os.getenv("REDIS_HOST", "redis-service")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/0")
