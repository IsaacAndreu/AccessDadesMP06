from flask import Blueprint, redirect, session, url_for

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    """
    Redirecciona l'usuari segons si està autenticat o no.
    - Si hi ha sessió activa, va al dashboard.
    - Si no, porta a la pàgina de login.
    """
    if "teacher_id" in session:
        return redirect(url_for("professors.dashboard"))
    return redirect(url_for("auth.login"))
