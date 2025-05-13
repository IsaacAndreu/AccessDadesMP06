from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import mongo

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "teacher_id" in session:
        flash("Ja estàs loguejat! Redirigint al dashboard...", "info")
        return redirect(url_for("professors.dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        teacher = mongo.db.professors.find_one({"email": email})

        if teacher and check_password_hash(teacher["password"], password):
            session["teacher_id"] = str(teacher["_id"])
            session["email"] = teacher["email"]
            session["rol"] = teacher.get("rol", "professor")
            session["is_admin"] = teacher.get("rol") == "admin"  # 🔥 aquesta línia permet el filtre al layout
            flash("Login correcte, redirigint al dashboard...", "success")
            return redirect(url_for("professors.dashboard"))
        else:
            flash("Credencials invàlides, torna-ho a provar.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            nom = request.form.get("nom")
            cognoms = request.form.get("cognoms")
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            if password != confirm_password:
                flash("Les contrasenyes no coincideixen.")
                return redirect(url_for("auth.register"))

            if mongo.db.professors.find_one({"email": email}):
                flash("Aquest email ja està registrat.")
                return redirect(url_for("auth.register"))

            hashed_password = generate_password_hash(password)
            teacher = {
                "nom": request.form.get("nom"),
                "cognoms": request.form.get("cognoms"),
                "email": email,
                "password": hashed_password,
                "rol": "professor"  # o "admin" si és el primer usuari, manualment
            }

            mongo.db.professors.insert_one(teacher)
            flash("Registre completat, ara pots iniciar sessió.")
            return redirect(url_for("auth.login"))

        except Exception as e:
            flash("Error en el registre: " + str(e))
            return redirect(url_for("auth.register"))

    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
