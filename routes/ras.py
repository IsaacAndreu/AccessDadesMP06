from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import login_required
from dao.ras_dao import *

ras_bp = Blueprint("ras", __name__)

@ras_bp.route("/llista")
@login_required
def llista_ras():
    ras = get_all_ras()
    return render_template("ras/llista.html", ras=ras)

@ras_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_ra_route():
    if request.method == "POST":
        nom = request.form.get("nom")
        ponderacio = request.form.get("ponderacio")

        if not nom or not ponderacio:
            flash("Tots els camps són obligatoris.", "error")
            return redirect(url_for("ras.add_ra_route"))

        try:
            add_ra(nom, ponderacio)
        except ValueError:
            flash("Ponderació invàlida.", "error")
            return redirect(url_for("ras.add_ra_route"))

        flash("RA afegit correctament.", "success")
        return redirect(url_for("ras.llista_ras"))

    return render_template("ras/add.html")

@ras_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_ra(id):
    ra = get_ra_by_id(id)
    if not ra:
        flash("RA no trobat.", "error")
        return redirect(url_for("ras.llista_ras"))

    if request.method == "POST":
        nom = request.form.get("nom")
        ponderacio = request.form.get("ponderacio")

        if not nom or not ponderacio:
            flash("Tots els camps són obligatoris.", "error")
            return redirect(url_for("ras.edit_ra", id=id))

        try:
            update_ra(id, nom, ponderacio)
        except ValueError:
            flash("Ponderació invàlida.", "error")
            return redirect(url_for("ras.edit_ra", id=id))

        flash("RA actualitzat correctament.", "success")
        return redirect(url_for("ras.llista_ras"))

    return render_template("ras/edit.html", ra=ra)

@ras_bp.route("/delete/<id>", methods=["POST"])
@login_required
def delete_ra_route(id):
    result = delete_ra(id)
    if result.deleted_count > 0:
        flash("RA eliminat correctament.", "success")
    else:
        flash("No s'ha pogut eliminar el RA.", "error")
    return redirect(url_for("ras.llista_ras"))
