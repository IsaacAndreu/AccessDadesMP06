from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import login_required, admin_required, mongo
from dao.professors_dao import *
from dao.professors_dao import get_grups_dict
from werkzeug.security import generate_password_hash
from bson import ObjectId
from werkzeug.utils import secure_filename
import os

professors_bp = Blueprint("professors", __name__)

# -- Vista principal del dashboard docent --
@professors_bp.route("/dashboard")
@login_required
def dashboard():
    teacher_id = session["teacher_id"]
    assignatures = get_assignatures_by_teacher(teacher_id)
    cicles_dict = get_cicles_dict()
    grups_dict = get_grups_dict()
    return render_template("professors/dashboard.html", assignatures=assignatures, cicles_dict=cicles_dict, grups_dict=grups_dict)

# -- Llista de cursos --
@professors_bp.route("/cursos", methods=["GET"])
@login_required
def llista_cursos():
    cursos = get_all_courses()
    return render_template("professors/llista_cursos.html", cursos=cursos)

# -- Crear un curs nou --
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

# -- Editar un curs --
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

# -- Eliminar un curs --
@professors_bp.route("/cursos/<course_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_course_route(course_id):
    result = delete_course(course_id)
    flash("Curs eliminat correctament." if result.deleted_count > 0 else "No s'ha pogut eliminar el curs.", "success" if result.deleted_count > 0 else "error")
    return redirect(url_for("professors.llista_cursos"))

# -- Llista de professors (només admin) --
@professors_bp.route("/list", methods=["GET"])
@login_required
@admin_required
def llista_professors():
    professors = get_all_professors()
    return render_template("professors/llista_professors.html", professors=professors)

# -- Afegir professor --
@professors_bp.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_professor_route():
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        cognoms = request.form.get("cognoms", "").strip()
        email = request.form.get("email", "").strip()

        if not nom or not cognoms or not email:
            flash("Nom, cognoms i email són obligatoris.", "error")
            return redirect(url_for("professors.add_professor_route"))

        add_professor(nom, cognoms, email)
        flash("Professor afegit correctament.", "success")
        return redirect(url_for("professors.llista_professors"))

    return render_template("professors/add_professor.html")

# -- Editar professor --
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

        if not nom or not cognoms or not email:
            flash("Tots els camps són obligatoris.", "error")
            return redirect(url_for("professors.edit_professor", prof_id=prof_id))

        update_professor(prof_id, nom, cognoms, email)
        flash("Professor actualitzat correctament.", "success")
        return redirect(url_for("professors.llista_professors"))

    return render_template("professors/edit_professor.html", professor=professor)

# -- Eliminar professor --
@professors_bp.route("/delete/<prof_id>", methods=["POST"])
@login_required
@admin_required
def delete_professor_route(prof_id):
    result = delete_professor(prof_id)
    flash("Professor eliminat correctament." if result.deleted_count > 0 else "No s'ha pogut eliminar el professor.", "success" if result.deleted_count > 0 else "error")
    return redirect(url_for("professors.llista_professors"))

# -- Perfil del professor loguejat --
@professors_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    professor_id = session["teacher_id"]
    professor = get_professor_by_id(professor_id)

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        cognoms = request.form.get("cognoms", "").strip()
        telefon = request.form.get("telefon", "").strip()
        tema = request.form.get("tema", "").strip()
        nova_password = request.form.get("nova_password")
        confirmar = request.form.get("confirmar")

        # Validació de la contrasenya nova
        if nova_password:
            if nova_password != confirmar:
                flash("Les contrasenyes no coincideixen.", "error")
                return redirect(url_for("professors.perfil"))
            hashed_password = generate_password_hash(nova_password)
        else:
            hashed_password = None

        # Validació i guardat de la imatge
        foto_filename = None
        foto = request.files.get("foto_perfil")
        if foto and foto.filename != "":
            filename = secure_filename(foto.filename)
            ext = filename.rsplit(".", 1)[-1].lower()
            if ext not in {"png", "jpg", "jpeg", "gif"}:
                flash("Format d'imatge no vàlid.", "error")
                return redirect(url_for("professors.perfil"))
            foto_path = os.path.join("static/uploads", filename)
            foto.save(foto_path)
            foto_filename = filename

        # Gestió de documents
        nou_document = request.files.get("nou_document")
        if nou_document and nou_document.filename != "":
            doc_filename = secure_filename(nou_document.filename)
            doc_ext = doc_filename.rsplit(".", 1)[-1].lower()
            if doc_ext not in {"pdf", "doc", "docx", "png", "jpg", "jpeg"}:
                flash("Format de document no vàlid.", "error")
                return redirect(url_for("professors.perfil"))
            doc_path = os.path.join("static/uploads", doc_filename)
            nou_document.save(doc_path)
            mongo.db.professors.update_one({"_id": ObjectId(professor_id)}, {"$addToSet": {"documents": doc_filename}})

        # Actualització del perfil
        update_professor_perfil(
            prof_id=professor_id,
            dades={"nom": nom, "cognoms": cognoms, "telefon": telefon, "tema": tema},
            nova_password=hashed_password,
            foto_filename=foto_filename
        )

        session["tema"] = tema
        flash("Perfil actualitzat correctament.", "success")
        return redirect(url_for("professors.perfil"))

    assignatures = get_assignatures_by_teacher(professor_id)
    return render_template("professors/perfil.html", professor=professor, assignatures=assignatures)

# -- Eliminar un document del perfil --
@professors_bp.route("/perfil/eliminar_document", methods=["POST"])
@login_required
def delete_document():
    doc_name = request.form.get("doc_name")
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

    flash("Document eliminat correctament." if result.modified_count > 0 else "No s'ha pogut eliminar el document.", "success" if result.modified_count > 0 else "error")
    return redirect(url_for("professors.perfil"))
