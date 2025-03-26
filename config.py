import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "alumne")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/centreEducatiuDB")
    SESSION_COOKIE_SECURE = False  # NO HTTPS en dev
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'