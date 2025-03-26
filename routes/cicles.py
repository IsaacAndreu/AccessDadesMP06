from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from extensions import mongo, login_required
cicles_bp = Blueprint("cicles", __name__)


@cicles_bp.route("/", methods=["GET"])
@login_required
def llista_cicles():
    # Recupera tots els cicles de la col·lecció "cicles"
    cicles = list(mongo.db.cicles.find())
    return render_template("cicles/llista.html", cicles=cicles)


@cicles_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_cicle():
    if request.method == "POST":
        nom = request.form.get("nom")
        descripcio = request.form.get("descripcio")

        if not nom:
            flash("El nom del cicle és obligatori.", "error")
            return redirect(url_for("cicles.add_cicle"))

        # Inserim el nou cicle
        nou_cicle = {
            "nom": nom.strip(),
            "descripcio": descripcio.strip() if descripcio else ""
        }
        mongo.db.cicles.insert_one(nou_cicle)
        flash("Cicle creat correctament.", "success")
        return redirect(url_for("cicles.llista_cicles"))

    return render_template("cicles/add.html")


@cicles_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_cicle(id):
    cicle = mongo.db.cicles.find_one({"_id": ObjectId(id)})
    if not cicle:
        flash("Cicle no trobat.", "error")
        return redirect(url_for("cicles.llista_cicles"))

    if request.method == "POST":
        nom = request.form.get("nom")
        descripcio = request.form.get("descripcio")

        if not nom:
            flash("El nom del cicle és obligatori.", "error")
            return redirect(url_for("cicles.edit_cicle", id=id))

        mongo.db.cicles.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "nom": nom.strip(),
                "descripcio": descripcio.strip() if descripcio else ""
            }}
        )
        flash("Cicle actualitzat correctament.", "success")
        return redirect(url_for("cicles.llista_cicles"))

    return render_template("cicles/edit.html", cicle=cicle)


@cicles_bp.route("/delete/<id>", methods=["POST"])
@login_required
def delete_cicle(id):
    mongo.db.cicles.delete_one({"_id": ObjectId(id)})
    flash("Cicle eliminat correctament.", "success")
    return redirect(url_for("cicles.llista_cicles"))
