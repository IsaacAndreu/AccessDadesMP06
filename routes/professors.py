from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import login_required
from dao.professors_dao import *

professors_bp = Blueprint("professors", __name__)


@professors_bp.route("/dashboard")
@login_required
def dashboard():
    teacher_id = session["teacher_id"]
    assignatures = get_assignatures_by_teacher(teacher_id)
    cicles_dict = get_cicles_dict()
    return render_template("professors/dashboard.html", assignatures=assignatures, cicles_dict=cicles_dict)


@professors_bp.route("/cursos", methods=["GET"])
@login_required
def llista_cursos():
    cursos = get_all_courses()
    return render_template("professors/llista_cursos.html", cursos=cursos)


@professors_bp.route("/create_course", methods=["GET", "POST"])
@login_required
def create_course():
    if request.method == "POST":
        course_name = request.form.get("course_name")
        description = request.form.get("description")

        if not course_name:
            flash("El nom del curs és obligatori.", "error")
            return redirect(url_for("professors.create_course"))

        add_course(course_name, description, session["teacher_id"])
        flash("Curs creat correctament!", "success")
        return redirect(url_for("professors.dashboard"))

    return render_template("professors/create_course.html")


@professors_bp.route("/cursos/<course_id>/edit", methods=["GET", "POST"])
@login_required
def edit_course(course_id):
    course = get_course_by_id(course_id)
    if not course:
        flash("Curs no trobat.", "error")
        return redirect(url_for("professors.llista_cursos"))

    if request.method == "POST":
        course_name = request.form.get("course_name")
        description = request.form.get("description")

        if not course_name:
            flash("El nom del curs és obligatori.", "error")
            return redirect(url_for("professors.edit_course", course_id=course_id))

        update_course(course_id, course_name, description)
        flash("Curs actualitzat correctament!", "success")
        return redirect(url_for("professors.llista_cursos"))

    return render_template("professors/edit_course.html", course=course)


@professors_bp.route("/cursos/<course_id>/delete", methods=["POST"])
@login_required
def delete_course_route(course_id):
    result = delete_course(course_id)
    if result.deleted_count > 0:
        flash("Curs eliminat correctament.", "success")
    else:
        flash("No s'ha pogut eliminar el curs (no trobat).", "error")
    return redirect(url_for("professors.llista_cursos"))


@professors_bp.route("/list", methods=["GET"])
@login_required
def llista_professors():
    professors = get_all_professors()
    return render_template("professors/llista_professors.html", professors=professors)


@professors_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_professor_route():
    if request.method == "POST":
        nom = request.form.get("nom")
        cognoms = request.form.get("cognoms")
        email = request.form.get("email")

        if not nom or not cognoms or not email:
            flash("Nom, cognoms i email són obligatoris.", "error")
            return redirect(url_for("professors.add_professor_route"))

        add_professor(nom, cognoms, email)
        flash("Professor afegit correctament.", "success")
        return redirect(url_for("professors.llista_professors"))

    return render_template("professors/add_professor.html")


@professors_bp.route("/edit/<prof_id>", methods=["GET", "POST"])
@login_required
def edit_professor(prof_id):
    professor = get_professor_by_id(prof_id)
    if not professor:
        flash("Professor no trobat.", "error")
        return redirect(url_for("professors.llista_professors"))

    if request.method == "POST":
        nom = request.form.get("nom")
        cognoms = request.form.get("cognoms")
        email = request.form.get("email")

        if not nom or not cognoms or not email:
            flash("Nom, cognoms i email són obligatoris.", "error")
            return redirect(url_for("professors.edit_professor", prof_id=prof_id))

        update_professor(prof_id, nom, cognoms, email)
        flash("Professor actualitzat correctament.", "success")
        return redirect(url_for("professors.llista_professors"))

    return render_template("professors/edit_professor.html", professor=professor)


@professors_bp.route("/delete/<prof_id>", methods=["POST"])
@login_required
def delete_professor_route(prof_id):
    result = delete_professor(prof_id)
    if result.deleted_count > 0:
        flash("Professor eliminat correctament.", "success")
    else:
        flash("No s'ha pogut eliminar el professor (no trobat).", "error")
    return redirect(url_for("professors.llista_professors"))
