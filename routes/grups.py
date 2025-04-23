from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from extensions import mongo, login_required

grups_bp = Blueprint("grups", __name__)


@grups_bp.route("/", methods=["GET"])
@login_required
def llista_grups():
    # Recuperem tots els grups de la col·lecció "grups"
    grups = list(mongo.db.grups.find())
    return render_template("grups/llista.html", grups=grups)


@grups_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_grup():
    if request.method == "POST":
        nom = request.form.get("nom")
        if not nom:
            flash("El nom del grup és obligatori.", "error")
            return redirect(url_for("grups.add_grup"))
        new_grup = {"nom": nom.strip()}
        mongo.db.grups.insert_one(new_grup)
        flash("Grup afegit correctament.", "success")
        return redirect(url_for("grups.llista_grups"))
    return render_template("grups/add.html")


@grups_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_grup(id):
    grup = mongo.db.grups.find_one({"_id": ObjectId(id)})
    if not grup:
        flash("Grup no trobat.", "error")
        return redirect(url_for("grups.llista_grups"))

    if request.method == "POST":
        nom = request.form.get("nom")
        if not nom:
            flash("El nom del grup és obligatori.", "error")
            return redirect(url_for("grups.edit_grup", id=id))
        mongo.db.grups.update_one({"_id": ObjectId(id)}, {"$set": {"nom": nom.strip()}})
        flash("Grup actualitzat correctament.", "success")
        return redirect(url_for("grups.llista_grups"))

    return render_template("grups/edit.html", grup=grup)


@grups_bp.route("/delete/<id>", methods=["POST"])
@login_required
def delete_grup(id):
    result = mongo.db.grups.delete_one({"_id": ObjectId(id)})
    if result.deleted_count > 0:
        flash("Grup eliminat correctament.", "success")
    else:
        flash("No s'ha pogut eliminar el grup.", "error")
    return redirect(url_for("grups.llista_grups"))
