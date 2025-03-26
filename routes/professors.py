from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson.objectid import ObjectId
from extensions import mongo, login_required

professors_bp = Blueprint("professors", __name__)

@professors_bp.route("/dashboard")
@login_required
def dashboard():
    teacher_id = ObjectId(session["teacher_id"])
    assignatures = list(mongo.db.assignatures.find({"professor_ids": teacher_id}))

    # Construïm un diccionari id_cicle → nom_cicle
    cicles = mongo.db.cicles.find()
    cicles_dict = {str(c["_id"]): c["nom"] for c in cicles}

    return render_template(
        "professors/dashboard.html",
        assignatures=assignatures,
        cicles_dict=cicles_dict
    )

# -------------------------
# CRUD de Cursos
# -------------------------
@professors_bp.route("/cursos", methods=["GET"])
@login_required
def llista_cursos():
    """Llista tots els cursos."""
    teacher_id = session.get("teacher_id")
    cursos = list(mongo.db.courses.find())
    return render_template("professors/llista_cursos.html", cursos=cursos)

@professors_bp.route("/create_course", methods=["GET", "POST"])
@login_required
def create_course():
    """Afegir nou curs"""
    if "teacher_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        course_name = request.form.get("course_name")
        description = request.form.get("description")

        if not course_name:
            flash("El nom del curs és obligatori.", "error")
            return redirect(url_for("professors.create_course"))

        new_course = {
            "course_name": course_name,
            "description": description,
            "teacher_id": session["teacher_id"]
        }
        mongo.db.courses.insert_one(new_course)
        flash("Curs creat correctament!", "success")
        return redirect(url_for("professors.dashboard"))

    return render_template("professors/create_course.html")

@professors_bp.route("/cursos/<course_id>/edit", methods=["GET", "POST"])
@login_required
def edit_course(course_id):
    """Editar un curs existent"""
    course = mongo.db.courses.find_one({"_id": ObjectId(course_id)})
    if not course:
        flash("Curs no trobat.", "error")
        return redirect(url_for("professors.llista_cursos"))

    if request.method == "POST":
        course_name = request.form.get("course_name")
        description = request.form.get("description")

        if not course_name:
            flash("El nom del curs és obligatori.", "error")
            return redirect(url_for("professors.edit_course", course_id=course_id))

        mongo.db.courses.update_one(
            {"_id": ObjectId(course_id)},
            {"$set": {"course_name": course_name, "description": description}}
        )
        flash("Curs actualitzat correctament!", "success")
        return redirect(url_for("professors.llista_cursos"))

    return render_template("professors/edit_course.html", course=course)

@professors_bp.route("/cursos/<course_id>/delete", methods=["POST"])
@login_required
def delete_course(course_id):
    """Eliminar un curs"""
    result = mongo.db.courses.delete_one({"_id": ObjectId(course_id)})
    if result.deleted_count > 0:
        flash("Curs eliminat correctament.", "success")
    else:
        flash("No s'ha pogut eliminar el curs (no trobat).", "error")
    return redirect(url_for("professors.llista_cursos"))

# -------------------------
# Vista de notes (placeholder)
# -------------------------
@professors_bp.route("/view_notes")
@login_required
def view_notes():
    """Vista placeholder per a notes"""
    if "teacher_id" not in session:
        return redirect(url_for("auth.login"))

    teacher_id = session["teacher_id"]
    notes = list(mongo.db.notes.find({"teacher_id": teacher_id}))
    return render_template("professors/view_notes.html", notes=notes)

# -------------------------
# CRUD de Professors
# -------------------------
@professors_bp.route("/list", methods=["GET"])
@login_required
def llista_professors():
    """Llista tots els professors"""
    professors = list(mongo.db.professors.find())
    return render_template("professors/llista_professors.html", professors=professors)

@professors_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_professor():
    """Afegir un nou professor"""
    if request.method == "POST":
        nom = request.form.get("nom")
        cognoms = request.form.get("cognoms")
        email = request.form.get("email")

        if not nom or not cognoms or not email:
            flash("Nom, cognoms i email són obligatoris.", "error")
            return redirect(url_for("professors.add_professor"))

        nou_professor = {
            "nom": nom.strip(),
            "cognoms": cognoms.strip(),
            "email": email.strip()
        }
        mongo.db.professors.insert_one(nou_professor)
        flash("Professor afegit correctament.", "success")
        return redirect(url_for("professors.llista_professors"))

    return render_template("professors/add_professor.html")

@professors_bp.route("/edit/<prof_id>", methods=["GET", "POST"])
@login_required
def edit_professor(prof_id):
    """Editar un professor existent"""
    professor = mongo.db.professors.find_one({"_id": ObjectId(prof_id)})
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

        mongo.db.professors.update_one(
            {"_id": ObjectId(prof_id)},
            {"$set": {
                "nom": nom.strip(),
                "cognoms": cognoms.strip(),
                "email": email.strip()
            }}
        )
        flash("Professor actualitzat correctament.", "success")
        return redirect(url_for("professors.llista_professors"))

    return render_template("professors/edit_professor.html", professor=professor)

@professors_bp.route("/delete/<prof_id>", methods=["POST"])
@login_required
def delete_professor(prof_id):
    """Eliminar un professor"""
    result = mongo.db.professors.delete_one({"_id": ObjectId(prof_id)})
    if result.deleted_count > 0:
        flash("Professor eliminat correctament.", "success")
    else:
        flash("No s'ha pogut eliminar el professor (no trobat).", "error")
    return redirect(url_for("professors.llista_professors"))
