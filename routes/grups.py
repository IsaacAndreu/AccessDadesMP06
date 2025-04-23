from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import login_required
from dao.grups_dao import (
    get_all_grups,
    add_grup,
    get_grup_by_id,
    update_grup,
    delete_grup
)

grups_bp = Blueprint("grups", __name__)


@grups_bp.route("/", methods=["GET"])
@login_required
def llista_grups():
    grups = get_all_grups()
    return render_template("grups/llista.html", grups=grups)


@grups_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_grup_route():
    if request.method == "POST":
        nom = request.form.get("nom")
        if not nom:
            flash("El nom del grup és obligatori.", "error")
            return redirect(url_for("grups.add_grup_route"))

        add_grup(nom)
        flash("Grup afegit correctament.", "success")
        return redirect(url_for("grups.llista_grups"))

    return render_template("grups/add.html")


@grups_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_grup(id):
    grup = get_grup_by_id(id)
    if not grup:
        flash("Grup no trobat.", "error")
        return redirect(url_for("grups.llista_grups"))

    if request.method == "POST":
        nom = request.form.get("nom")
        if not nom:
            flash("El nom del grup és obligatori.", "error")
            return redirect(url_for("grups.edit_grup", id=id))

        update_grup(id, nom)
        flash("Grup actualitzat correctament.", "success")
        return redirect(url_for("grups.llista_grups"))

    return render_template("grups/edit.html", grup=grup)


@grups_bp.route("/delete/<id>", methods=["POST"])
@login_required
def delete_grup_route(id):
    result = delete_grup(id)
    if result.deleted_count > 0:
        flash("Grup eliminat correctament.", "success")
    else:
        flash("No s'ha pogut eliminar el grup.", "error")
    return redirect(url_for("grups.llista_grups"))
