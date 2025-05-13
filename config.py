import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "alumne")

    # MongoDB
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017/centreEducatiuDB")

    # Oracle DB amb SQLAlchemy
    SQLALCHEMY_DATABASE_URI = "oracle+cx_oracle://ADMIN:ADMINPASSWORD@localhost:1521/XE"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cookies
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
