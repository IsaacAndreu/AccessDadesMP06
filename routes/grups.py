import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import login_required, admin_required
from dao.oracle_grups_dao import (
    get_grups, get_grup_by_id,
    add_grup, update_grup, delete_grup_by_id
)

grups_bp = Blueprint("grups", __name__)

def validar_nom_grup(nom):
    """Valida que el nom del grup només contingui lletres i espais."""
    return bool(re.match(r"^[A-Za-zÀ-ÿ\s]+$", nom))

def validar_i_obtenir_nom(form, ruta_error, id=None):
    """Funció auxiliar per validar el nom i retornar el valor o redirigir amb error."""
    nom = form.get("nom", "").strip()
    if not nom:
        flash("El nom del grup és obligatori.", "error")
        return redirect(url_for(ruta_error, **({"id": id} if id else {}))), None
    if not validar_nom_grup(nom):
        flash("El nom del grup només pot contenir lletres i espais.", "error")
        return redirect(url_for(ruta_error, **({"id": id} if id else {}))), None
    return None, nom

@grups_bp.route("/", methods=["GET"])
@login_required
def llista_grups():
    grups = get_grups()
    return render_template("grups/llista.html", grups=grups)

@grups_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_grup_route():
    if request.method == "POST":
        err_redirect, nom = validar_i_obtenir_nom(request.form, "grups.add_grup_route")
        if err_redirect:
            return err_redirect

        add_grup(nom)
        flash("Grup afegit correctament.", "success")
        return redirect(url_for("grups.llista_grups"))

    return render_template("grups/afegir.html")

@grups_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_grup(id):
    grup = get_grup_by_id(id)
    if not grup:
        flash("Grup no trobat.", "error")
        return redirect(url_for("grups.llista_grups"))

    if request.method == "POST":
        err_redirect, nom = validar_i_obtenir_nom(request.form, "grups.edit_grup", id=id)
        if err_redirect:
            return err_redirect

        update_grup(id, nom)
        flash("Grup actualitzat correctament.", "success")
        return redirect(url_for("grups.llista_grups"))

    return render_template("grups/edit.html", grup=grup)

@grups_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_grup_route(id):
    delete_grup_by_id(id)
    flash("Grup eliminat correctament.", "success")
    return redirect(url_for("grups.llista_grups"))
