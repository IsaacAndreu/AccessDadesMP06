from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import login_required
from dao.ras_dao import *

ras_bp = Blueprint("ras", __name__)

# -- Vista per llistar tots els RAs --
@ras_bp.route("/llista")
@login_required
def llista_ras():
    ras = get_all_ras()
    return render_template("ras/llista.html", ras=ras)

# -- Afegir un RA --
@ras_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_ra_route():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        ponderacio = request.form.get("ponderacio", "").strip()

        if not nom or not ponderacio:
            flash("Tots els camps són obligatoris.", "error")
            return redirect(url_for("ras.add_ra_route"))

        try:
            ponderacio_val = float(ponderacio)
            if not (0 <= ponderacio_val <= 100):
                raise ValueError("Fora de rang")
            add_ra(nom, ponderacio_val)
        except ValueError:
            flash("La ponderació ha de ser un número entre 0 i 100.", "error")
            return redirect(url_for("ras.add_ra_route"))

        flash("RA afegit correctament.", "success")
        return redirect(url_for("ras.llista_ras"))

    return render_template("ras/afegir.html")

# -- Editar un RA --
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

        if not nom or not ponderacio:
            flash("Tots els camps són obligatoris.", "error")
            return redirect(url_for("ras.edit_ra", id=id))

        try:
            ponderacio_val = float(ponderacio)
            if not (0 <= ponderacio_val <= 100):
                raise ValueError("Fora de rang")
            update_ra(id, nom, ponderacio_val)
        except ValueError:
            flash("La ponderació ha de ser un número entre 0 i 100.", "error")
            return redirect(url_for("ras.edit_ra", id=id))

        flash("RA actualitzat correctament.", "success")
        return redirect(url_for("ras.llista_ras"))

    return render_template("ras/edit.html", ra=ra)

# -- Eliminar un RA --
@ras_bp.route("/delete/<id>", methods=["POST"])
@login_required
def delete_ra_route(id):
    result = delete_ra(id)
    if result and result.deleted_count > 0:
        flash("RA eliminat correctament.", "success")
    else:
        flash("No s'ha pogut eliminar el RA.", "error")
    return redirect(url_for("ras.llista_ras"))
