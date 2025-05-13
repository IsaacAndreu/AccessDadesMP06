from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
import cx_Oracle
import os
from dotenv import load_dotenv
from flask import session, redirect, url_for, flash
from functools import wraps

load_dotenv()  # Carrega variables d'entorn des del fitxer .env

mongo = PyMongo()
db = SQLAlchemy()
from flask_babel import Babel

babel = Babel()
def oracle_connection():
    return cx_Oracle.connect(
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        dsn=os.getenv("ORACLE_DSN")
    )

from functools import wraps
from flask import session, redirect, url_for

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "teacher_id" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "teacher_id" not in session or session.get("rol") != "admin":
            flash("Accés restringit a administradors.", "error")
            return redirect(url_for("professors.dashboard"))
        return view(*args, **kwargs)
    return wrapped
