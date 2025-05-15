from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import login_required
from dao.ras_dao import *

ras_bp = Blueprint("ras", __name__)

def validar_ra_form(nom, ponderacio):
    if not nom or not ponderacio:
        return False, "Tots els camps són obligatoris."
    try:
        val = float(ponderacio)
        if not (0 <= val <= 100):
            return False, "La ponderació ha de ser un número entre 0 i 100."
    except ValueError:
        return False, "La ponderació ha de ser un número entre 0 i 100."
    return True, val


@ras_bp.route("/llista")
@login_required
def llista_ras():
    ras = get_all_ras()
    return render_template("ras/llista.html", ras=ras)


@ras_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_ra_route():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        ponderacio = request.form.get("ponderacio", "").strip()

        valid, result = validar_ra_form(nom, ponderacio)
        if not valid:
            flash(result, "error")
            return redirect(url_for("ras.add_ra_route"))

        add_ra(nom, result)
        flash("RA afegit correctament.", "success")
        return redirect(url_for("ras.llista_ras"))

    return render_template("ras/afegir.html")


@ras_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_ra(id):
    ra = get_ra_by_id(id)
    if not ra:
        flash("RA no trobat.", "error")
        return redirect(url_for("ras.llista_ras"))

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        ponderacio = request.form.get("ponderacio", "").strip()

        valid, result = validar_ra_form(nom, ponderacio)
        if not valid:
            flash(result, "error")
            return redirect(url_for("ras.edit_ra", id=id))

        update_ra(id, nom, result)
        flash("RA actualitzat correctament.", "success")
        return redirect(url_for("ras.llista_ras"))

    return render_template("ras/edit.html", ra=ra)


@ras_bp.route("/delete/<id>", methods=["POST"])
@login_required
def delete_ra_route(id):
    result = delete_ra(id)
    if result and result.deleted_count > 0:
        flash("RA eliminat correctament.", "success")
    else:
        flash("No s'ha pogut eliminar el RA.", "error")
    return redirect(url_for("ras.llista_ras"))
