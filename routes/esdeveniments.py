import re
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from extensions import login_required, admin_required, mongo
from bson.objectid import ObjectId

esdeveniments_bp = Blueprint("esdeveniments", __name__, url_prefix="/esdeveniments")

def validar_titol(cadena):
    """
    Valida que el títol només contingui:
      - lletres (incloent accents)
      - dígits (0–9)
      - espais
      - apòstrofs (')
    """
    patro = r"^[A-Za-zÀ-ÿ0-9'\s]+$"
    return bool(re.match(patro, cadena))

def validar_dades_esdeveniment(titol, inici):
    """Valida les dades essencials d'un esdeveniment, retorna (ok, missatge)."""
    if not titol or not inici:
        return False, "El títol i la data d'inici són obligatoris."
    if not validar_titol(titol):
        return False, "El títol només pot contenir lletres i espais."
    return True, ""

def obtenir_professor_id():
    """Obté el professor_id de la sessió."""
    return session.get("teacher_id")

@esdeveniments_bp.route("/")
@login_required
def llistar_esdeveniments():
    """Vista principal amb el calendari."""
    return render_template("esdeveniments/llista.html")

@esdeveniments_bp.route("/api")
@login_required
def obtenir_esdeveniments():
    """Retorna els esdeveniments del professor actual en JSON per FullCalendar."""
    professor_id = obtenir_professor_id()
    esdeveniments = list(mongo.db.esdeveniments.find({"professor_id": professor_id}))
    for e in esdeveniments:
        e["_id"] = str(e["_id"])
        e["id"] = e["_id"]  # FullCalendar espera clau "id"
    return jsonify(esdeveniments)

@esdeveniments_bp.route("/afegir", methods=["GET", "POST"])
@login_required
def afegir_esdeveniment():
    if request.method == "POST":
        titol = request.form.get("titol", "").strip()
        inici = request.form.get("inici", "").strip()
        fi = request.form.get("fi", "").strip()
        descripcio = request.form.get("descripcio", "").strip()

        valid, msg = validar_dades_esdeveniment(titol, inici)
        if not valid:
            flash(msg, "error")
            return redirect(url_for("esdeveniments.afegir_esdeveniment"))

        nou_esdeveniment = {
            "title": titol,
            "start": inici,
            "end": fi,
            "description": descripcio,
            "professor_id": obtenir_professor_id()
        }
        mongo.db.esdeveniments.insert_one(nou_esdeveniment)
        flash("Esdeveniment afegit correctament.", "success")
        return redirect(url_for("esdeveniments.llistar_esdeveniments"))

    return render_template("esdeveniments/formulari.html")

@esdeveniments_bp.route("/afegir-ajax", methods=["POST"])
@login_required
def afegir_des_del_calendari():
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    start = data.get("start", "").strip()

    valid, msg = validar_dades_esdeveniment(title, start)
    if not valid:
        return jsonify({"status": "error", "message": msg}), 400

    nou_esdeveniment = {
        "title": title,
        "start": start,
        "professor_id": obtenir_professor_id()
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
        titol = request.form.get("titol", "").strip()
        inici = request.form.get("inici", "").strip()
        fi = request.form.get("fi", "").strip()
        descripcio = request.form.get("descripcio", "").strip()

        valid, msg = validar_dades_esdeveniment(titol, inici)
        if not valid:
            flash(msg, "error")
            return redirect(url_for("esdeveniments.editar_esdeveniment", id=id))

        nova_dades = {
            "title": titol,
            "start": inici,
            "end": fi,
            "description": descripcio
        }
        mongo.db.esdeveniments.update_one({"_id": ObjectId(id)}, {"$set": nova_dades})
        flash("Esdeveniment actualitzat.", "success")
        return redirect(url_for("esdeveniments.llistar_esdeveniments"))

    return render_template("esdeveniments/editar.html", esdeveniment=esdeveniment)

@esdeveniments_bp.route("/eliminar/<id>", methods=["POST"])
@login_required
def eliminar_esdeveniment(id):
    professor_id = obtenir_professor_id()
    mongo.db.esdeveniments.delete_one({"_id": ObjectId(id), "professor_id": professor_id})
    flash("Esdeveniment eliminat.", "success")
    return redirect(url_for("esdeveniments.llistar_esdeveniments"))
