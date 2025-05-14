from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import login_required, admin_required
from dao.oracle_cicles_dao import (
    get_cicles,
    add_cicle,
    get_cicle_by_id,
    update_cicle,
    delete_cicle_by_id
)

cicles_bp = Blueprint("cicles", __name__)

# Mostra la llista de cicles disponibles
@cicles_bp.route("/", methods=["GET"])
@login_required
def llista_cicles():
    cicles = get_cicles()
    return render_template("cicles/llista.html", cicles=cicles)

# Afegeix un nou cicle (GET per mostrar formulari, POST per afegir)
@cicles_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_cicle_route():
    if request.method == "POST":
        nom = request.form.get("nom")
        descripcio = request.form.get("descripcio")

        if not nom:
            flash("El nom del cicle és obligatori.", "error")
            return redirect(url_for("cicles.add_cicle_route"))

        add_cicle(nom.strip(), descripcio.strip() if descripcio else "")
        flash("Cicle creat correctament.", "success")
        return redirect(url_for("cicles.llista_cicles"))

    return render_template("cicles/afegir.html")

# Edita un cicle existent
@cicles_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_cicle(id):
    cicle = get_cicle_by_id(id)
    if not cicle:
        flash("Cicle no trobat.", "error")
        return redirect(url_for("cicles.llista_cicles"))

    if request.method == "POST":
        nom = request.form.get("nom")
        descripcio = request.form.get("descripcio")

        if not nom:
            flash("El nom del cicle és obligatori.", "error")
            return redirect(url_for("cicles.edit_cicle", id=id))

        update_cicle(id, nom.strip(), descripcio.strip() if descripcio else "")
        flash("Cicle actualitzat correctament.", "success")
        return redirect(url_for("cicles.llista_cicles"))

    return render_template("cicles/edit.html", cicle=cicle)

# Elimina un cicle identificat pel seu ID (només via POST)
@cicles_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_cicle_route(id):
    delete_cicle_by_id(id)
    flash("Cicle eliminat correctament.", "success")
    return redirect(url_for("cicles.llista_cicles"))
