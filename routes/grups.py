import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import login_required, admin_required
from dao.oracle_grups_dao import (
    get_grups, get_grup_by_id,
    add_grup, update_grup, delete_grup_by_id
)

grups_bp = Blueprint("grups", __name__)

# Funció per validar que el nom del grup només contingui lletres i espais
def validar_nom_grup(nom):
    if not re.match("^[A-Za-zÀ-ÿ\s]+$", nom):  # Accepta lletres i espais
        return False
    return True

# Llista tots els grups disponibles
@grups_bp.route("/", methods=["GET"])
@login_required
def llista_grups():
    grups = get_grups()
    return render_template("grups/llista.html", grups=grups)

# Afegeix un nou grup (GET per mostrar el formulari, POST per processar-lo)
@grups_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_grup_route():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()

        # Validació del nom del grup
        if not nom:
            flash("El nom del grup és obligatori.", "error")
            return redirect(url_for("grups.add_grup_route"))

        if not validar_nom_grup(nom):
            flash("El nom del grup només pot contenir lletres i espais.", "error")
            return redirect(url_for("grups.add_grup_route"))

        add_grup(nom)
        flash("Grup afegit correctament.", "success")
        return redirect(url_for("grups.llista_grups"))

    return render_template("grups/afegir.html")

# Edita un grup existent
@grups_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_grup(id):
    grup = get_grup_by_id(id)
    if not grup:
        flash("Grup no trobat.", "error")
        return redirect(url_for("grups.llista_grups"))

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()

        # Validació del nom del grup
        if not nom:
            flash("El nom del grup és obligatori.", "error")
            return redirect(url_for("grups.edit_grup", id=id))

        if not validar_nom_grup(nom):
            flash("El nom del grup només pot contenir lletres i espais.", "error")
            return redirect(url_for("grups.edit_grup", id=id))

        update_grup(id, nom)
        flash("Grup actualitzat correctament.", "success")
        return redirect(url_for("grups.llista_grups"))

    return render_template("grups/edit.html", grup=grup)

# Elimina un grup a partir del seu ID (només accessible via POST)
@grups_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_grup_route(id):
    delete_grup_by_id(id)
    flash("Grup eliminat correctament.", "success")
    return redirect(url_for("grups.llista_grups"))
