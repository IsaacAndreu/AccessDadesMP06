import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import mongo

auth_bp = Blueprint("auth", __name__)

# Funció per validar nom i cognoms (només lletres i espais)
def validar_nom_cognoms(cadena):
    if not re.match("^[A-Za-zÀ-ÿ\s]+$", cadena):  # Accepta lletres, accents i espais
        return False
    return True

# Funció per validar l'email
def validar_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Evita mostrar el formulari si l'usuari ja està autenticat
    if "teacher_id" in session:
        flash("Ja estàs loguejat! Redirigint al dashboard...", "info")
        return redirect(url_for("professors.dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Validació de l'email
        if not validar_email(email):
            flash("Email no vàlid.", "error")
            return redirect(url_for("auth.login"))

        teacher = mongo.db.professors.find_one({"email": email})

        # Validació de credencials
        if teacher and check_password_hash(teacher["password"], password):
            session["teacher_id"] = str(teacher["_id"])
            session["email"] = teacher["email"]
            session["rol"] = teacher.get("rol", "professor")
            session["is_admin"] = teacher.get("rol") == "admin"
            flash("Login correcte, redirigint al dashboard...", "success")
            return redirect(url_for("professors.dashboard"))

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

            # Validació dels camps nom i cognoms
            if not validar_nom_cognoms(nom) or not validar_nom_cognoms(cognoms):
                flash("Nom i cognoms només poden contenir lletres i espais.", "error")
                return redirect(url_for("auth.register"))

            # Validació de contrasenya
            if password != confirm_password:
                flash("Les contrasenyes no coincideixen.", "error")
                return redirect(url_for("auth.register"))

            # Validació de l'email
            if not validar_email(email):
                flash("Email no vàlid.", "error")
                return redirect(url_for("auth.register"))

            # Comprovació si l'email ja existeix
            if mongo.db.professors.find_one({"email": email}):
                flash("Aquest email ja està registrat.", "error")
                return redirect(url_for("auth.register"))

            hashed_password = generate_password_hash(password)

            teacher = {
                "nom": nom,
                "cognoms": cognoms,
                "email": email,
                "password": hashed_password,
                "rol": "professor"  # Canviar manualment si cal crear un admin
            }

            mongo.db.professors.insert_one(teacher)
            flash("Registre completat, ara pots iniciar sessió.", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            flash("Error en el registre: " + str(e), "error")
            return redirect(url_for("auth.register"))

    return render_template("auth/register.html")

@auth_bp.route("/logout")
def logout():
    # Tanca sessió esborrant la sessió activa
    session.clear()
    return redirect(url_for("auth.login"))
