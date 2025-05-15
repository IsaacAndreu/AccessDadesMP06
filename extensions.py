# Importació de paquets necessaris per la configuració de la base de dades i connexions externes
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
import cx_Oracle
import os
from dotenv import load_dotenv
from flask import session, redirect, url_for, flash
from functools import wraps

# Carregar les variables d'entorn des del fitxer .env
load_dotenv()

# Inicialització de les extensions per a MongoDB i SQLAlchemy
mongo = PyMongo()
db = SQLAlchemy()

# Importació de Babel per a la traducció i localització
from flask_babel import Babel
babel = Babel()

# Funció per establir connexió amb la base de dades Oracle
def oracle_connection():
    """
    Estableix i retorna una connexió a la base de dades Oracle mitjançant cx_Oracle.
    Utilitza variables d'entorn per obtenir les credencials de connexió.
    """
    return cx_Oracle.connect(
        user=os.getenv("ORACLE_USER"),  # Usuari de la base de dades Oracle
        password=os.getenv("ORACLE_PASSWORD"),  # Contrasenya de la base de dades Oracle
        dsn=os.getenv("ORACLE_DSN")  # DSN de la base de dades Oracle
    )

# Decorador per a la verificació de l'usuari autenticat
def login_required(view):
    """
    Decorador que redirigeix a l'usuari a la pàgina de login si no està autenticat.
    Assegura que l'usuari ha iniciat sessió abans d'accedir a la vista protegida.
    """
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "teacher_id" not in session:  # Comprova si el professor està autenticat
            return redirect(url_for("auth.login"))  # Redirigeix a la pàgina de login si no està autenticat
        return view(*args, **kwargs)
    return wrapped

# Decorador per a la verificació del rol d'administrador
def admin_required(view):
    """
    Decorador que només permet l'accés a la vista si l'usuari és administrador.
    Redirigeix a la pàgina del dashboard si l'usuari no té el rol d'administrador.
    """
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "teacher_id" not in session or session.get("rol") != "admin":  # Comprova si l'usuari és administrador
            flash("Accés restringit a administradors.", "error")  # Mostra un missatge d'error si l'usuari no té permís
            return redirect(url_for("professors.dashboard"))  # Redirigeix al dashboard si no és administrador
        return view(*args, **kwargs)
    return wrapped
