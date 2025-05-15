import os

class Config:
    """
    Aquesta classe conté la configuració general per a l'aplicació Flask.
    Les variables d'entorn s'utilitzen per a configurar la base de dades, les cookies, etc.
    """

    # --- Clau secreta per protegir les sessions de Flask ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "alumne")  # Utilitza la variable d'entorn SECRET_KEY per la seguretat de la sessió

    # --- Configuració per MongoDB ---
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017/centreEducatiuDB")  # URI de connexió a MongoDB

    # --- Configuració per Oracle DB amb SQLAlchemy ---
    # Per utilitzar Oracle amb SQLAlchemy, utilitzem cx_Oracle com a controlador.
    SQLALCHEMY_DATABASE_URI = "oracle+cx_oracle://ADMIN:ADMINPASSWORD@localhost:1521/XE"  # Configuració estàtica de connexió a Oracle
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Desactiva el seguiment de les modificacions per evitar advertències

    # --- Configuració de cookies per la sessió ---
    SESSION_COOKIE_SECURE = False  # Hauria de ser True en un entorn de producció per garantir la seguretat de les cookies
    SESSION_COOKIE_HTTPONLY = True  # Evita que les cookies siguin accessibles mitjançant JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protegeix contra atacs CSRF limitant l'enviament de cookies en sol·licituds creuades

