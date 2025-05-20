import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from extensions import login_required, admin_required
from dao.assignatures_dao import (
    get_assignatures,
    get_courses_dict,
    get_courses,
    get_professors,
    add_assignatura,
    get_assignatura_by_id,
    update_assignatura,
    delete_assignatura_by_id,
)
from dao.oracle_academics_dao import (
    get_grups_oracle as get_grups,
    get_cicles_oracle as get_cicles,
)

assignatures_bp = Blueprint("assignatures", __name__)

# --- Funcions auxiliars ---

def validar_nom(nom):
    """Accepta lletres, accents, espais, números i dos punts."""
    return bool(re.match(r"^[A-Za-zÀ-ÿ0-9\s:]+$", nom))


def carregar_dades_formulari():
    """
    Retorna les dades necessàries per omplir el formulari:
      - cursos (MongoDB)
      - grups (Oracle ORM)
      - cicles (Oracle ORM)
      - professors (MongoDB)
    """
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

    # 1. Nom
    if not nom or not validar_nom(nom):
        errors.append("El nom de l'assignatura no és vàlid.")

    # 2. Cursos
    if not courses:
        errors.append("Has de seleccionar almenys un curs.")

    # 3. Grups
    if not grups:
        errors.append("Has de seleccionar almenys un grup.")

    # 4. Cicle
    if cicle_id is None:
        errors.append("Has de seleccionar un cicle.")

    # 5. Any acadèmic
    if not any_academic:
        errors.append("Has de seleccionar un any acadèmic.")

    # 6. Professors
    if not professor_ids:
        errors.append("Has d'assignar almenys un professor.")

    # 7. RAs
    total = sum(ra["ponderacio"] for ra in ras)
    if total != 100:
        errors.append(f"La suma de les ponderacions dels RAs ha de ser 100% (ara: {total}%).")

    return errors
# --- Rutes ---

@assignatures_bp.route("/", methods=["GET"])
@login_required
def llista_assignatures():
    assignatures = get_assignatures()
    cursos_dict = get_courses_dict()

    # Converteix cicle_id i grups a int
    for a in assignatures:
        try:
            a["cicle_id"] = int(a.get("cicle_id", 0))
        except (ValueError, TypeError):
            a["cicle_id"] = None

        raw_grups = a.get("grups", [])
        a["grups"] = []
        for g in raw_grups:
            try:
                a["grups"].append(int(g))
            except (ValueError, TypeError):
                continue

    # Obtenim les llistes d'ORM de l'Oracle
    cicles = get_cicles()
    grups = get_grups()

    # Creem els diccionaris amb atributs .id i .nom
    cicles_dict = {c.id: c.nom for c in cicles}
    grups_dict = {g.id: g.nom for g in grups}

    return render_template(
        "assignatures/llista.html",
        assignatures=assignatures,
        cursos_dict=cursos_dict,
        cicles_dict=cicles_dict,
        grups_dict=grups_dict,
    )


@assignatures_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_assignatura_route():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        descripcio = request.form.get("descripcio", "").strip()
        ras = construir_ras(
            request.form.getlist("ra_name[]"),
            request.form.getlist("ra_percentage[]"),
        )

        courses = request.form.getlist("courses[]")

        # Converteix els grups seleccionats a enters
        grups_raw = request.form.getlist("grups[]")
        grups = []
        for g in grups_raw:
            try:
                grups.append(int(g))
            except (ValueError, TypeError):
                continue

        # Converteix cicle_id a enter
        cicle_id_raw = request.form.get("cicle_id", "")
        try:
            cicle_id = int(cicle_id_raw)
        except (ValueError, TypeError):
            cicle_id = None

        any_academic = request.form.get("any_academic", "").strip()
        professor_ids = request.form.getlist("professor_ids[]")

        errors = validar_formulari_assignatura(
            nom, courses, grups, cicle_id, any_academic, professor_ids, ras
        )
        if errors:
            for e in errors:
                flash(e, "error")
            return redirect(url_for("assignatures.add_assignatura_route"))

        nova_assignatura = {
            "nom": nom,
            "descripcio": descripcio,
            "ras": ras,
            "courses": courses,
            "grups": grups,
            "cicle_id": cicle_id,
            "any_academic": any_academic,
            "professor_ids": [ObjectId(pid) for pid in professor_ids],
        }
        add_assignatura(nova_assignatura)

        flash("Assignatura afegida correctament.", "success")
        return redirect(url_for("assignatures.llista_assignatures"))

    # GET: transformem tant cicles com grups a dicts amb _id perquè el template faci {{ g._id }}
    courses_list, grups_list, cicles_list, professors = carregar_dades_formulari()
    # grups_list és llista d’ORM -> convertim a dicts
    grups_list = [{"_id": str(g.id), "nom": g.nom} for g in grups_list]
    # cicles_list ho fèiem ja abans; fem el mateix
    cicles_list = [{"_id": str(c.id), "nom": c.nom} for c in cicles_list]

    return render_template(
        "assignatures/afegir.html",
        courses=courses_list,
        grups=grups_list,
        cicles=cicles_list,
        professors=professors,
    )

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
        ras = construir_ras(
            request.form.getlist("ra_name[]"),
            request.form.getlist("ra_percentage[]"),
        )

        courses = request.form.getlist("courses[]")

        # Converteix els grups seleccionats a enters
        grups_raw = request.form.getlist("grups[]")
        grups = []
        for g in grups_raw:
            try:
                grups.append(int(g))
            except (ValueError, TypeError):
                continue

        # Converteix cicle_id a enter
        cicle_id_raw = request.form.get("cicle_id", "")
        try:
            cicle_id = int(cicle_id_raw)
        except (ValueError, TypeError):
            cicle_id = None

        any_academic = request.form.get("any_academic", "").strip()
        professor_ids = request.form.getlist("professor_ids[]")

        errors = validar_formulari_assignatura(
            nom, courses, grups, cicle_id, any_academic, professor_ids, ras
        )
        if errors:
            for e in errors:
                flash(e, "error")
            return redirect(url_for("assignatures.edit_assignatura", id=id))

        assignatura_actualitzada = {
            "nom": nom,
            "descripcio": descripcio,
            "ras": ras,
            "courses": courses,
            "grups": grups,
            "cicle_id": cicle_id,
            "any_academic": any_academic,
            "professor_ids": [ObjectId(pid) for pid in professor_ids],
        }
        update_assignatura(id, assignatura_actualitzada)
        flash("Assignatura actualitzada correctament.", "success")
        return redirect(url_for("assignatures.llista_assignatures"))

    # GET: preparem dades per al formulari
    courses_list, grups_orm, cicles_orm, professors = carregar_dades_formulari()

    # Convertim ORM instances a dicts amb _id com a string
    grups_list = [{"_id": str(g.id), "nom": g.nom} for g in grups_orm]
    cicles_list = [{"_id": str(c.id), "nom": c.nom} for c in cicles_orm]

    # Preparem també assignatura.grups perquè el template marqui els selected
    # i cicle_id perquè el select el tingui seleccionat
    assignatura_grups_str = [str(g) for g in assignatura.get("grups", [])]
    assignatura_cicle_str = str(assignatura.get("cicle_id", ""))

    return render_template(
        "assignatures/edit.html",
        assignatura=assignatura,
        courses=courses_list,
        grups=grups_list,
        cicles=cicles_list,
        professors=professors,
        selected_grups=assignatura_grups_str,
        selected_cicle=assignatura_cicle_str
    )


@assignatures_bp.route("/delete/<id>", methods=["POST"])
@login_required
@admin_required
def delete_assignatura(id):
    delete_assignatura_by_id(id)
    flash("Assignatura eliminada correctament.", "success")
    return redirect(url_for("assignatures.llista_assignatures"))
