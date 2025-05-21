from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import login_required, admin_required, mongo
from dao.professors_dao import *
from dao.oracle_academics_dao import get_cicles_oracle, get_grups_oracle
from werkzeug.security import generate_password_hash
from bson import ObjectId
from werkzeug.utils import secure_filename
import os
import re

professors_bp = Blueprint("professors", __name__)

# Funció per validar noms i cognoms (només lletres i espais)
def validar_nom_cognom(nom):
    return bool(re.match(r"^[A-Za-zÀ-ÿ]+(?: [A-Za-zÀ-ÿ]+)*$", nom))

# Nova funció per validar el telèfon (només dígits)
def validar_telefon(telefon):
    """
    Només permet dígits (i cadena buida si és opcional).
    """
    return bool(re.fullmatch(r"\d*", telefon))

def guardar_fitxer(fitxer, carpeta, extensions_permeses):
    """Guarda un fitxer si és vàlid i retorna el nom del fitxer, o (None, error)."""
    if fitxer and fitxer.filename:
        filename = secure_filename(fitxer.filename)
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext not in extensions_permeses:
            return None, f"Format no vàlid. Extensions permeses: {', '.join(extensions_permeses)}"
        path = os.path.join("static", carpeta, filename)
        fitxer.save(path)
        return filename, None
    return None, None

def validar_camps_professor(nom, cognoms, email):
    if not (nom and cognoms and email):
        return False, "Nom, cognoms i email són obligatoris."
    if not validar_nom_cognom(nom):
        return False, "Nom invàlid. Només es permeten lletres i espais."
    if not validar_nom_cognom(cognoms):
        return False, "Cognoms invàlids. Només es permeten lletres i espais."
    return True, None


@professors_bp.route("/dashboard")
@login_required
def dashboard():
    teacher_id   = session["teacher_id"]
    assignatures = get_assignatures_by_teacher(teacher_id)

    for a in assignatures:
        # Convertim cicle_id a int o None
        try:
            a["cicle_id"] = int(a.get("cicle_id", None))
        except (ValueError, TypeError):
            a["cicle_id"] = None

        # Prenem la llista original de grups (pot venir com a strings)
        raw_grups = a.get("grups", [])

        # Convertem-la a ints, descartant valors invàlids
        clean_grups = []
        for g in raw_grups:
            try:
                clean_grups.append(int(g))
            except (ValueError, TypeError):
                continue

        # Finalment, assignem la llista neta
        a["grups"] = clean_grups

    # Preparem els diccionaris per la plantilla
    cicles = get_cicles_oracle()
    grups  = get_grups_oracle()
    cicles_dict = {c.id: c.nom for c in cicles}
    grups_dict  = {g.id: g.nom for g in grups}

    return render_template(
        "professors/dashboard.html",
        assignatures=assignatures,
        cicles_dict=cicles_dict,
        grups_dict=grups_dict
    )


@professors_bp.route("/cursos")
@login_required
def llista_cursos():
    cursos = get_all_courses()
    return render_template("professors/llista_cursos.html", cursos=cursos)


@professors_bp.route("/create_course", methods=["GET", "POST"])
@login_required
@admin_required
def create_course():
    if request.method == "POST":
        course_name = request.form.get("course_name", "").strip()
        description = request.form.get("description", "").strip()

        if not course_name:
            flash("El nom del curs és obligatori.", "error")
            return redirect(url_for("professors.create_course"))

        add_course(course_name, description, session["teacher_id"])
        flash("Curs creat correctament!", "success")
        return redirect(url_for("professors.dashboard"))

    return render_template("professors/create_course.html")


@professors_bp.route("/cursos/<course_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_course(course_id):
    course = get_course_by_id(course_id)
    if not course:
        flash("Curs no trobat.", "error")
        return redirect(url_for("professors.llista_cursos"))

    if request.method == "POST":
        course_name = request.form.get("course_name", "").strip()
        description = request.form.get("description", "").strip()

        if not course_name:
            flash("El nom del curs és obligatori.", "error")
            return redirect(url_for("professors.edit_course", course_id=course_id))

        update_course(course_id, course_name, description)
        flash("Curs actualitzat correctament!", "success")
        return redirect(url_for("professors.llista_cursos"))

    return render_template("professors/edit_course.html", course=course)


@professors_bp.route("/cursos/<course_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_course_route(course_id):
    result = delete_course(course_id)
    if result.deleted_count > 0:
        flash("Curs eliminat correctament.", "success")
    else:
        flash("No s'ha pogut eliminar el curs.", "error")
    return redirect(url_for("professors.llista_cursos"))


@professors_bp.route("/list")
@login_required
@admin_required
def llista_professors():
    professors = get_all_professors()
    return render_template("professors/llista_professors.html", professors=professors)


@professors_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_professor_route():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        cognoms = request.form.get("cognoms", "").strip()
        email = request.form.get("email", "").strip()

        valid, error = validar_camps_professor(nom, cognoms, email)
        if not valid:
            flash(error, "error")
            return redirect(url_for("professors.add_professor_route"))

        add_professor(nom, cognoms, email)
        flash("Professor afegit correctament.", "success")
        return redirect(url_for("professors.llista_professors"))

    return render_template("professors/add_professor.html")


@professors_bp.route("/edit/<prof_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_professor(prof_id):
    professor = get_professor_by_id(prof_id)
    if not professor:
        flash("Professor no trobat.", "error")
        return redirect(url_for("professors.llista_professors"))

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        cognoms = request.form.get("cognoms", "").strip()
        email = request.form.get("email", "").strip()

        valid, error = validar_camps_professor(nom, cognoms, email)
        if not valid:
            flash(error, "error")
            return redirect(url_for("professors.edit_professor", prof_id=prof_id))

        update_professor(prof_id, nom, cognoms, email)
        flash("Professor actualitzat correctament.", "success")
        return redirect(url_for("professors.llista_professors"))

    return render_template("professors/edit_professor.html", professor=professor)


@professors_bp.route("/delete/<prof_id>", methods=["POST"])
@login_required
@admin_required
def delete_professor_route(prof_id):
    result = delete_professor(prof_id)
    if result.deleted_count > 0:
        flash("Professor eliminat correctament.", "success")
    else:
        flash("No s'ha pogut eliminar el professor.", "error")
    return redirect(url_for("professors.llista_professors"))


@professors_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    professor_id = session["teacher_id"]
    professor = get_professor_by_id(professor_id)

    if request.method == "POST":
        nom          = request.form.get("nom", "").strip()
        cognoms      = request.form.get("cognoms", "").strip()
        telefon      = request.form.get("telefon", "").strip()
        tema         = request.form.get("tema", "").strip()
        nova_password = request.form.get("nova_password")
        confirmar     = request.form.get("confirmar")

        # Validem el telèfon: només dígits
        if not validar_telefon(telefon):
            flash("El telèfon només pot contenir números.", "error")
            return redirect(url_for("professors.perfil"))

        if nova_password and nova_password != confirmar:
            flash("Les contrasenyes no coincideixen.", "error")
            return redirect(url_for("professors.perfil"))

        hashed_password = generate_password_hash(nova_password) if nova_password else None

        # Pujar foto de perfil
        foto, error = guardar_fitxer(
            request.files.get("foto_perfil"),
            "uploads",
            {"png", "jpg", "jpeg", "gif"}
        )
        if error:
            flash(error, "error")
            return redirect(url_for("professors.perfil"))

        # Pujar nou document (si n'hi ha)
        nou_document, error = guardar_fitxer(
            request.files.get("nou_document"),
            "uploads",
            {"pdf", "doc", "docx", "png", "jpg", "jpeg"}
        )
        if error:
            flash(error, "error")
            return redirect(url_for("professors.perfil"))
        if nou_document:
            mongo.db.professors.update_one(
                {"_id": ObjectId(professor_id)},
                {"$addToSet": {"documents": nou_document}}
            )

        # Actualitzem les dades restants
        dades = {"nom": nom, "cognoms": cognoms, "telefon": telefon, "tema": tema}
        update_professor_perfil(
            prof_id=professor_id,
            dades=dades,
            nova_password=hashed_password,
            foto_filename=foto
        )

        session["tema"] = tema
        flash("Perfil actualitzat correctament.", "success")
        return redirect(url_for("professors.perfil"))

    assignatures = get_assignatures_by_teacher(professor_id)
    return render_template(
        "professors/perfil.html",
        professor=professor,
        assignatures=assignatures
    )


@professors_bp.route("/perfil/eliminar_document", methods=["POST"])
@login_required
def delete_document():
    doc_name    = request.form.get("doc_name")
    professor_id = session["teacher_id"]

    if not doc_name:
        flash("Cap document indicat per eliminar.", "error")
        return redirect(url_for("professors.perfil"))

    result = mongo.db.professors.update_one(
        {"_id": ObjectId(professor_id)},
        {"$pull": {"documents": doc_name}}
    )

    file_path = os.path.join("static/uploads", doc_name)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            flash(f"Error eliminant el fitxer: {e}", "error")

    if result.modified_count > 0:
        flash("Document eliminat correctament.", "success")
    else:
        flash("No s'ha pogut eliminar el document.", "error")
    return redirect(url_for("professors.perfil"))
