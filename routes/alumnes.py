from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import login_required
from dao.alumnes_dao import (
    get_alumnes_filtrats,
    get_grups,
    get_cicles,
    add_alumne,
    get_alumne_by_id,
    update_alumne,
    delete_alumne_by_id
)
from bson.objectid import ObjectId

alumnes_bp = Blueprint("alumnes", __name__)


@alumnes_bp.route("/", methods=["GET"])
@login_required
def llista_alumnes():
    grup_id = request.args.get("grup_id", "")
    cicle_id = request.args.get("cicle_id", "")

    alumnes = get_alumnes_filtrats(grup_id, cicle_id)
    grups = get_grups()
    grups_dict = {str(g["_id"]): g["nom"] for g in grups}
    cicles = get_cicles()
    cicles_dict = {str(c["_id"]): c["nom"] for c in cicles}

    return render_template(
        "alumnes/llista.html",
        alumnes=alumnes,
        grups=grups,
        grups_dict=grups_dict,
        cicles=cicles,
        cicles_dict=cicles_dict,
        grup_id_seleccionat=grup_id,
        cicle_id_seleccionat=cicle_id
    )


@alumnes_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_alumne_route():
    if request.method == "POST":
        nom = request.form.get("nom")
        cognoms = request.form.get("cognoms")
        email = request.form.get("email")
        grup = request.form.get("grup")
        cicle_id = request.form.get("cicle_id")
        curs = request.form.get("curs")

        if not nom or not cognoms or not grup or not cicle_id or not curs:
            flash("Nom, cognoms, grup, cicle i curs són obligatoris.", "error")
            return redirect(url_for("alumnes.add_alumne_route"))

        add_alumne(nom, cognoms, email, grup, cicle_id, curs)
        flash("Alumne afegit correctament.", "success")
        return redirect(url_for("alumnes.llista_alumnes"))

    grups = get_grups()
    cicles = get_cicles()
    return render_template("alumnes/add.html", grups=grups, cicles=cicles)


@alumnes_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_alumne(id):
    alumne = get_alumne_by_id(id)
    if not alumne:
        flash("Alumne no trobat.", "error")
        return redirect(url_for("alumnes.llista_alumnes"))

    if request.method == "POST":
        nom = request.form.get("nom")
        cognoms = request.form.get("cognoms")
        email = request.form.get("email")
        grup = request.form.get("grup")
        cicle_id = request.form.get("cicle_id")
        curs = request.form.get("curs")

        if not nom or not cognoms or not grup or not cicle_id or not curs:
            flash("Nom, cognoms, grup, cicle i curs són obligatoris.", "error")
            return redirect(url_for("alumnes.edit_alumne", id=id))

        update_alumne(id, nom, cognoms, email, grup, cicle_id, curs)
        flash("Alumne actualitzat correctament.", "success")
        return redirect(url_for("alumnes.llista_alumnes"))

    grups = get_grups()
    cicles = get_cicles()
    return render_template("alumnes/edit.html", alumne=alumne, grups=grups, cicles=cicles)


@alumnes_bp.route("/delete/<id>", methods=["POST"])
@login_required
def delete_alumne(id):
    delete_alumne_by_id(id)
    flash("Alumne eliminat correctament.")
    return redirect(url_for("alumnes.llista_alumnes"))
