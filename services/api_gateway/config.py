import os


class Config:
    SERVICE_NAME = "api-gateway"
    SERVICE_PORT = int(os.environ.get("SERVICE_PORT", 8080))

    # Route prefix -> downstream base URL (equivalent to Spring Cloud Gateway routes)
    ROUTES = {
        "/api/users": os.environ.get("USER_SERVICE_URL", "http://localhost:8081"),
        "/api/appointments": os.environ.get("APPOINTMENT_SERVICE_URL", "http://localhost:8082"),
        "/api/doctors": os.environ.get("DOCTOR_SERVICE_URL", "http://localhost:8083"),
        "/api/patients": os.environ.get("PATIENT_SERVICE_URL", "http://localhost:8084"),
    }

    PUBLIC_PATHS = {
        "/api/users/register",
        "/api/users/login",
        "/actuator/health",
    }

    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    RATE_LIMIT = os.environ.get("RATE_LIMIT", "20 per 10 seconds")
