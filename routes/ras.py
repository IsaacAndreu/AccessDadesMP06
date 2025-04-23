from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from extensions import mongo, login_required

ras_bp = Blueprint("ras", __name__)

@ras_bp.route("/llista")
@login_required
def llista_ras():
    # Recuperem tots els RAs de la col·lecció "ras"
    ras = list(mongo.db.ras.find())
    return render_template("ras/llista.html", ras=ras)

@ras_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_ra():
    if request.method == "POST":
        nom = request.form.get("nom")
        ponderacio = request.form.get("ponderacio")
        if not nom or not ponderacio:
            flash("Tots els camps són obligatoris.", "error")
            return redirect(url_for("ras.add_ra"))
        try:
            ponderacio = float(ponderacio)
        except ValueError:
            flash("Ponderació invàlida.", "error")
            return redirect(url_for("ras.add_ra"))
        new_ra = {
            "nom": nom.strip(),
            "ponderacio": ponderacio
        }
        mongo.db.ras.insert_one(new_ra)
        flash("RA afegit correctament.", "success")
        return redirect(url_for("ras.llista_ras"))
    return render_template("ras/add.html")

@ras_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_ra(id):
    ra = mongo.db.ras.find_one({"_id": ObjectId(id)})
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
            ponderacio = float(ponderacio)
        except ValueError:
            flash("Ponderació invàlida.", "error")
            return redirect(url_for("ras.edit_ra", id=id))
        mongo.db.ras.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"nom": nom.strip(), "ponderacio": ponderacio}}
        )
        flash("RA actualitzat correctament.", "success")
        return redirect(url_for("ras.llista_ras"))
    return render_template("ras/edit.html", ra=ra)

@ras_bp.route("/delete/<id>", methods=["POST"])
@login_required
def delete_ra(id):
    result = mongo.db.ras.delete_one({"_id": ObjectId(id)})
    if result.deleted_count > 0:
        flash("RA eliminat correctament.", "success")
    else:
        flash("No s'ha pogut eliminar el RA.", "error")
    return redirect(url_for("ras.llista_ras"))
