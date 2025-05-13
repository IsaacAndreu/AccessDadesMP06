from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from extensions import login_required, admin_required, mongo
from bson.objectid import ObjectId
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
#                                                      👆 AIXÒ ÉS EL QUE FALTAVA
from extensions import login_required, admin_required, mongo
from bson.objectid import ObjectId
from datetime import datetime

esdeveniments_bp = Blueprint("esdeveniments", __name__, url_prefix="/esdeveniments")


@esdeveniments_bp.route("/")
@login_required
def llistar_esdeveniments():
    """Vista principal que carrega el calendari."""
    return render_template("esdeveniments/llista.html")


@esdeveniments_bp.route("/api")
@login_required
def obtenir_esdeveniments():
    professor_id = session["teacher_id"]
    esdeveniments = list(mongo.db.esdeveniments.find({"professor_id": professor_id}))
    for e in esdeveniments:
        e["_id"] = str(e["_id"])
        e["id"] = e["_id"]  # FullCalendar espera "id"
    return jsonify(esdeveniments)

@esdeveniments_bp.route("/afegir", methods=["GET", "POST"])
@login_required
@admin_required
def afegir_esdeveniment():
    """Formulari per afegir un nou esdeveniment."""
    if request.method == "POST":
        titol = request.form.get("titol")
        inici = request.form.get("inici")
        fi = request.form.get("fi")
        descripcio = request.form.get("descripcio")

        if not titol or not inici:
            flash("El títol i la data d'inici són obligatoris.", "error")
            return redirect(url_for("esdeveniments.afegir_esdeveniment"))

        nou_esdeveniment = {
            "title": titol,
            "start": inici,
            "end": fi,
            "description": descripcio,
            "professor_id": session["teacher_id"]
        }

        mongo.db.esdeveniments.insert_one(nou_esdeveniment)
        flash("Esdeveniment afegit correctament!", "success")
        return redirect(url_for("esdeveniments.llistar_esdeveniments"))

    return render_template("esdeveniments/formulari.html")

@esdeveniments_bp.route("/afegir-ajax", methods=["POST"])
@login_required
def afegir_des_del_calendari():
    data = request.get_json()
    title = data.get("title")
    start = data.get("start")

    if not title or not start:
        return jsonify({"status": "error", "message": "Falten dades"}), 400

    nou_esdeveniment = {
        "title": title,
        "start": start,
        "professor_id": session["teacher_id"]
    }

    mongo.db.esdeveniments.insert_one(nou_esdeveniment)
    return jsonify({"status": "ok"})
@esdeveniments_bp.route("/editar/<id>", methods=["GET", "POST"])
@login_required
def editar_esdeveniment(id):
    esdeveniment = mongo.db.esdeveniments.find_one({"_id": ObjectId(id)})

    if not esdeveniment:
        flash("Esdeveniment no trobat.", "error")
        return redirect(url_for("esdeveniments.llistar_esdeveniments"))

    if request.method == "POST":
        titol = request.form.get("titol")
        inici = request.form.get("inici")
        fi = request.form.get("fi")
        descripcio = request.form.get("descripcio")

        nova_dades = {
            "title": titol,
            "start": inici,
            "end": fi,
            "description": descripcio
        }

        mongo.db.esdeveniments.update_one({"_id": ObjectId(id)}, {"$set": nova_dades})
        flash("Esdeveniment actualitzat!", "success")
        return redirect(url_for("esdeveniments.llistar_esdeveniments"))

    return render_template("esdeveniments/editar.html", esdeveniment=esdeveniment)


@esdeveniments_bp.route("/eliminar/<id>", methods=["POST"])
@login_required
def eliminar_esdeveniment(id):
    professor_id = session["teacher_id"]
    mongo.db.esdeveniments.delete_one({"_id": ObjectId(id), "professor_id": professor_id})
    flash("Esdeveniment eliminat.", "success")
    return redirect(url_for("esdeveniments.llistar_esdeveniments"))
