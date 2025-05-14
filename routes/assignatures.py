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

# Carrega les dades necessàries per al formulari (reutilitzat a afegir i editar)
def carregar_dades_formulari():
    return get_courses(), get_grups(), get_cicles(), get_professors()

# Llista totes les assignatures disponibles
@assignatures_bp.route("/", methods=["GET"])
@login_required
def llista_assignatures():
    assignatures = get_assignatures()
    cursos_dict = get_courses_dict()
    return render_template("assignatures/llista.html", assignatures=assignatures, cursos_dict=cursos_dict)

# Afegeix una nova assignatura (GET per mostrar formulari, POST per processar-lo)
@assignatures_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_assignatura_route():
    if request.method == "POST":
        nom = request.form.get("nom")
        descripcio = request.form.get("descripcio")
        ra_names = request.form.getlist("ra_name[]")
        ra_percentages = request.form.getlist("ra_percentage[]")

        # Construcció dels resultats d'aprenentatge amb validació de ponderació
        ras = []
        for name, perc in zip(ra_names, ra_percentages):
            if name.strip():
                try:
                    percentage = float(perc)
                except ValueError:
                    percentage = 0.0
                ras.append({"nom": name.strip(), "ponderacio": percentage})

        courses = request.form.getlist("courses[]")
        grups = request.form.getlist("grups[]")
        cicle_id = request.form.get("cicle_id")
        any_academic = request.form.get("any_academic")
        professor_ids = request.form.getlist("professor_ids[]")

        total = sum(ra["ponderacio"] for ra in ras)
        if total != 100:
            flash(f"La suma de les ponderacions dels RAs ha de ser 100%. Actualment suma: {total}%", "error")
            return redirect(url_for("assignatures.add_assignatura_route"))

        if not nom or not courses or not grups or not cicle_id or not any_academic or not professor_ids:
            flash("Tots els camps són obligatoris.", "error")
            return redirect(url_for("assignatures.add_assignatura_route"))

        new_assignatura = {
            "nom": nom.strip(),
            "descripcio": descripcio.strip() if descripcio else "",
            "ras": ras,
            "courses": courses,
            "grups": grups,
            "cicle_id": ObjectId(cicle_id),
            "any_academic": any_academic,
            "professor_ids": [ObjectId(pid) for pid in professor_ids]
        }

        add_assignatura(new_assignatura)
        flash("Assignatura afegida correctament.", "success")
        return redirect(url_for("assignatures.llista_assignatures"))

    # GET: mostra el formulari amb les dades necessàries
    courses_list, grups_list, cicles, professors = carregar_dades_formulari()
    return render_template("assignatures/afegir.html",
                           courses=courses_list,
                           grups=grups_list,
                           cicles=cicles,
                           professors=professors)

# Edita una assignatura existent (GET per mostrar el formulari, POST per actualitzar)
@assignatures_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_assignatura(id):
    assignatura = get_assignatura_by_id(id)
    if not assignatura:
        flash("Assignatura no trobada.", "error")
        return redirect(url_for("assignatures.llista_assignatures"))

    if request.method == "POST":
        nom = request.form.get("nom")
        descripcio = request.form.get("descripcio")
        ra_names = request.form.getlist("ra_name[]")
        ra_percentages = request.form.getlist("ra_percentage[]")

        ras = []
        for name, perc in zip(ra_names, ra_percentages):
            if name.strip():
                try:
                    percentage = float(perc)
                except ValueError:
                    percentage = 0.0
                ras.append({"nom": name.strip(), "ponderacio": percentage})

        courses = request.form.getlist("courses[]")
        grups = request.form.getlist("grups[]")
        cicle_id = request.form.get("cicle_id")
        any_academic = request.form.get("any_academic")
        professor_ids = request.form.getlist("professor_ids[]")

        if not nom or not courses or not grups or not cicle_id or not any_academic or not professor_ids:
            flash("Tots els camps són obligatoris.", "error")
            return redirect(url_for("assignatures.edit_assignatura", id=id))

        total = sum(ra["ponderacio"] for ra in ras)
        if total != 100:
            flash(f"La suma de les ponderacions dels RAs ha de ser 100%. Actualment suma: {total}%", "error")
            return redirect(url_for("assignatures.edit_assignatura", id=id))

        updated_data = {
            "nom": nom.strip(),
            "descripcio": descripcio.strip() if descripcio else "",
            "ras": ras,
            "courses": courses,
            "grups": grups,
            "cicle_id": ObjectId(cicle_id),
            "any_academic": any_academic,
            "professor_ids": [ObjectId(pid) for pid in professor_ids]
        }

        update_assignatura(id, updated_data)
        flash("Assignatura actualitzada correctament.", "success")
        return redirect(url_for("assignatures.llista_assignatures"))

    # GET: mostra el formulari d'edició amb les dades actuals
    courses_list, grups_list, cicles, professors = carregar_dades_formulari()
    return render_template("assignatures/edit.html",
                           assignatura=assignatura,
                           courses=courses_list,
                           grups=grups_list,
                           cicles=cicles,
                           professors=professors)

# Elimina una assignatura a partir del seu identificador
@assignatures_bp.route("/delete/<id>", methods=["POST"])
@login_required
@admin_required
def delete_assignatura(id):
    delete_assignatura_by_id(id)
    flash("Assignatura eliminada correctament.", "success")
    return redirect(url_for("assignatures.llista_assignatures"))
