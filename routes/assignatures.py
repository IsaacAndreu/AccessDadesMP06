import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from extensions import login_required, admin_required
from dao.assignatures_dao import (
    get_assignatures, get_courses_dict, get_courses,
    get_grups, get_cicles, get_professors,
    add_assignatura, get_assignatura_by_id,
    update_assignatura, delete_assignatura_by_id
)

assignatures_bp = Blueprint("assignatures", __name__)

# --- Funcions auxiliars ---

def validar_nom(nom):
    """Accepta lletres, accents, espais, números i dos punts."""
    return bool(re.match(r"^[A-Za-zÀ-ÿ0-9\s:]+$", nom))

def carregar_dades_formulari():
    return get_courses(), get_grups(), get_cicles(), get_professors()

def construir_ras(ra_names, ra_percentages):
    ras = []
    for name, perc in zip(ra_names, ra_percentages):
        if name.strip():
            try:
                percentage = float(perc)
            except ValueError:
                percentage = 0.0
            ras.append({"nom": name.strip(), "ponderacio": percentage})
    return ras

def validar_formulari_assignatura(nom, courses, grups, cicle_id, any_academic, professor_ids, ras):
    errors = []
    if not nom or not validar_nom(nom):
        errors.append("El nom de l'assignatura només pot contenir lletres, espais i caràcters vàlids.")
    if not all([courses, grups, cicle_id, any_academic, professor_ids]):
        errors.append("Tots els camps són obligatoris.")
    total = sum(ra["ponderacio"] for ra in ras)
    if total != 100:
        errors.append(f"La suma de les ponderacions dels RAs ha de ser 100%. Actualment suma: {total}%.")
    return errors

# --- Rutes ---

@assignatures_bp.route("/", methods=["GET"])
@login_required
def llista_assignatures():
    assignatures = get_assignatures()
    cursos_dict = get_courses_dict()
    return render_template("assignatures/llista.html", assignatures=assignatures, cursos_dict=cursos_dict)

@assignatures_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_assignatura_route():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        descripcio = request.form.get("descripcio", "").strip()
        ra_names = request.form.getlist("ra_name[]")
        ra_percentages = request.form.getlist("ra_percentage[]")

        ras = construir_ras(ra_names, ra_percentages)

        courses = request.form.getlist("courses[]")
        grups = request.form.getlist("grups[]")
        cicle_id = request.form.get("cicle_id")
        any_academic = request.form.get("any_academic")
        professor_ids = request.form.getlist("professor_ids[]")

        errors = validar_formulari_assignatura(nom, courses, grups, cicle_id, any_academic, professor_ids, ras)
        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for("assignatures.add_assignatura_route"))

        nova_assignatura = {
            "nom": nom,
            "descripcio": descripcio,
            "ras": ras,
            "courses": courses,
            "grups": grups,
            "cicle_id": ObjectId(cicle_id),
            "any_academic": any_academic,
            "professor_ids": [ObjectId(pid) for pid in professor_ids]
        }

        add_assignatura(nova_assignatura)
        flash("Assignatura afegida correctament.", "success")
        return redirect(url_for("assignatures.llista_assignatures"))

    courses_list, grups_list, cicles, professors = carregar_dades_formulari()
    return render_template("assignatures/afegir.html",
                           courses=courses_list,
                           grups=grups_list,
                           cicles=cicles,
                           professors=professors)

@assignatures_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_assignatura(id):
    assignatura = get_assignatura_by_id(id)
    if not assignatura:
        flash("Assignatura no trobada.", "error")
        return redirect(url_for("assignatures.llista_assignatures"))

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        descripcio = request.form.get("descripcio", "").strip()
        ra_names = request.form.getlist("ra_name[]")
        ra_percentages = request.form.getlist("ra_percentage[]")

        ras = construir_ras(ra_names, ra_percentages)

        courses = request.form.getlist("courses[]")
        grups = request.form.getlist("grups[]")
        cicle_id = request.form.get("cicle_id")
        any_academic = request.form.get("any_academic")
        professor_ids = request.form.getlist("professor_ids[]")

        errors = validar_formulari_assignatura(nom, courses, grups, cicle_id, any_academic, professor_ids, ras)
        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for("assignatures.edit_assignatura", id=id))

        assignatura_actualitzada = {
            "nom": nom,
            "descripcio": descripcio,
            "ras": ras,
            "courses": courses,
            "grups": grups,
            "cicle_id": ObjectId(cicle_id),
            "any_academic": any_academic,
            "professor_ids": [ObjectId(pid) for pid in professor_ids]
        }

        update_assignatura(id, assignatura_actualitzada)
        flash("Assignatura actualitzada correctament.", "success")
        return redirect(url_for("assignatures.llista_assignatures"))

    courses_list, grups_list, cicles, professors = carregar_dades_formulari()
    return render_template("assignatures/edit.html",
                           assignatura=assignatura,
                           courses=courses_list,
                           grups=grups_list,
                           cicles=cicles,
                           professors=professors)

@assignatures_bp.route("/delete/<id>", methods=["POST"])
@login_required
@admin_required
def delete_assignatura(id):
    delete_assignatura_by_id(id)
    flash("Assignatura eliminada correctament.", "success")
    return redirect(url_for("assignatures.llista_assignatures"))
