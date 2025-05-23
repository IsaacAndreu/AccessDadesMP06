from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import login_required, admin_required
from dao.oracle_alumnes_dao import (
    get_alumnes_filtrats, get_grups, get_cicles,
    add_alumne, get_alumne_by_id, update_alumne, delete_alumne_by_id
)

alumnes_bp = Blueprint("alumnes", __name__, url_prefix="/alumnes")

# --- Funcions auxiliars ---
def carregar_grups_i_cicles():
    return get_grups(), get_cicles()

def nom_valid(text):
    import re
    return re.fullmatch(r"[A-Za-zÀ-ÿ\s'-]{2,50}", text) is not None

def form_data_valida(nom, cognoms, grup_id, cicle_id, curs):
    errors = []
    if not all([nom, cognoms, grup_id, cicle_id, curs]):
        errors.append("Nom, cognoms, grup, cicle i curs són obligatoris.")
    if not nom_valid(nom) or not nom_valid(cognoms):
        errors.append("El nom i cognoms només poden contenir lletres i espais.")
    return errors


# --- Rutes ---
@alumnes_bp.route("/", methods=["GET"])
@login_required
def llista_alumnes():
    grup_id = request.args.get("grup_id", "")
    cicle_id = request.args.get("cicle_id", "")

    alumnes = get_alumnes_filtrats(grup_id, cicle_id)
    grups, cicles = carregar_grups_i_cicles()

    grups_dict = {g.id: g.nom for g in grups}
    cicles_dict = {c.id: c.nom for c in cicles}

    return render_template(
        "alumnes/llista.html",
        alumnes=alumnes,
        grups=grups,
        grups_dict=grups_dict,
        cicles=cicles,
        cicles_dict=cicles_dict,
        grup_id_seleccionat=grup_id,
        cicle_id_seleccionat=cicle_id
    )


@alumnes_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_alumne_route():
    grups, cicles = carregar_grups_i_cicles()

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        cognoms = request.form.get("cognoms", "").strip()
        email = request.form.get("email", "").strip()
        grup_id = request.form.get("grup_id")
        cicle_id = request.form.get("cicle_id")
        curs = request.form.get("curs")

        errors = form_data_valida(nom, cognoms, grup_id, cicle_id, curs)
        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for("alumnes.add_alumne_route"))

        try:
            add_alumne(nom, cognoms, email, grup_id, cicle_id, curs)
            flash("Alumne afegit correctament.", "success")
            return redirect(url_for("alumnes.llista_alumnes"))
        except Exception as e:
            flash(f"Error afegint alumne: {e}", "error")

    return render_template("alumnes/afegir.html", grups=grups, cicles=cicles)


@alumnes_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_alumne(id):
    alumne = get_alumne_by_id(id)
    if not alumne:
        flash("Alumne no trobat.", "error")
        return redirect(url_for("alumnes.llista_alumnes"))

    grups, cicles = carregar_grups_i_cicles()

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        cognoms = request.form.get("cognoms", "").strip()
        email = request.form.get("email", "").strip()
        grup_id = request.form.get("grup_id")
        cicle_id = request.form.get("cicle_id")
        curs = request.form.get("curs")

        errors = form_data_valida(nom, cognoms, grup_id, cicle_id, curs)
        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for("alumnes.edit_alumne", id=id))

        try:
            update_alumne(id, nom, cognoms, email, grup_id, cicle_id, curs)
            flash("Alumne actualitzat correctament.", "success")
            return redirect(url_for("alumnes.llista_alumnes"))
        except Exception as e:
            flash(f"Error actualitzant alumne: {e}", "error")

    return render_template("alumnes/edit.html", alumne=alumne, grups=grups, cicles=cicles)


@alumnes_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_alumne(id):
    try:
        delete_alumne_by_id(id)
        flash("Alumne eliminat correctament.", "success")
    except Exception as e:
        flash(f"Error eliminant alumne: {e}", "error")

    return redirect(url_for("alumnes.llista_alumnes"))
