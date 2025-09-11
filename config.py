import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET", "supersecret")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET", "change-this")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    DB_PATH = "users.db"
    DOCKER_HOST = os.environ.get("DOCKER_HOST", "unix:///var/run/docker.sock")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5000))

