from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from extensions import mongo, login_required

assignatures_bp = Blueprint("assignatures", __name__)

@assignatures_bp.route("/", methods=["GET"])
@login_required
def llista_assignatures():
    assignatures = list(mongo.db.assignatures.find())

    # Creem un diccionari amb els cursos existents per evitar múltiples consultes a la BD
    cursos_dict = {str(course["_id"]): course["course_name"] for course in mongo.db.courses.find()}

    return render_template("assignatures/llista.html", assignatures=assignatures, cursos_dict=cursos_dict)

@assignatures_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_assignatura():
    if request.method == "POST":
        nom = request.form.get("nom")
        descripcio = request.form.get("descripcio")

        # 1. Recuperem noms i ponderacions dels ras
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

        # 2. Recuperem la resta de camps (courses, grups, etc.)
        courses = request.form.getlist("courses[]")
        grups = request.form.getlist("grups[]")
        cicle_id = request.form.get("cicle_id")
        any_academic = request.form.get("any_academic")  # Nou camp per l'any acadèmic
        professor_ids = request.form.getlist("professor_ids[]")

        # (Opcional) Comprovem que la suma de ras sigui 100
        total = sum([ra["ponderacio"] for ra in ras])
        if total != 100:
            flash(f"La suma de les ponderacions dels RAs ha de ser 100%. Actualment suma: {total}%", "error")
            return redirect(url_for("assignatures.add_assignatura"))

        # 3. Validacions mínimes
        if not nom or not courses or not grups or not cicle_id or not any_academic or not professor_ids:
            flash("Tots els camps són obligatoris.", "error")
            return redirect(url_for("assignatures.add_assignatura"))

        # 4. Convertim els professor_ids a ObjectId
        professor_ids_obj = [ObjectId(pid) for pid in professor_ids]

        # 5. Creem el diccionari per inserir
        new_assignatura = {
            "nom": nom.strip(),
            "descripcio": descripcio.strip() if descripcio else "",
            "ras": ras,  # llista de RA processats
            "courses": courses,
            "grups": grups,
            "cicle_id": ObjectId(cicle_id),
            "any_academic": any_academic,
            "professor_ids": professor_ids_obj
        }

        mongo.db.assignatures.insert_one(new_assignatura)
        flash("Assignatura afegida correctament.", "success")
        return redirect(url_for("assignatures.llista_assignatures"))

    # GET: Recuperem dades per al formulari
    courses_list = list(mongo.db.courses.find())
    grups_list = list(mongo.db.grups.find())
    # Si no hi ha grups, inserim per defecte "A" i "B"
    if not grups_list:
        default_grups = [{"nom": "A"}, {"nom": "B"}]
        mongo.db.grups.insert_many(default_grups)
        grups_list = list(mongo.db.grups.find())

    cicles = list(mongo.db.cicles.find())
    professors = list(mongo.db.professors.find())
    return render_template("assignatures/add.html",
                           courses=courses_list,
                           grups=grups_list,
                           cicles=cicles,
                           professors=professors)

@assignatures_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_assignatura(id):
    assignatura = mongo.db.assignatures.find_one({"_id": ObjectId(id)})
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
        curs = request.form.getlist("curs[]")
        professor_ids = request.form.getlist("professor_ids[]")

        if not nom or not courses or not grups or not cicle_id or not curs or not professor_ids:
            flash("Tots els camps són obligatoris.", "error")
            return redirect(url_for("assignatures.edit_assignatura", id=id))

        total = sum([ra["ponderacio"] for ra in ras])
        if total != 100:
            flash(f"La suma de les ponderacions dels RAs ha de ser 100%. Actualment suma: {total}%", "error")
            return redirect(url_for("assignatures.edit_assignatura", id=id))

        professor_ids_obj = [ObjectId(pid) for pid in professor_ids]

        mongo.db.assignatures.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "nom": nom.strip(),
                "descripcio": descripcio.strip() if descripcio else "",
                "ras": ras,
                "courses": courses,
                "grups": grups,
                "cicle_id": ObjectId(cicle_id),
                "curs": curs,
                "professor_ids": professor_ids_obj
            }}
        )
        flash("Assignatura actualitzada correctament.", "success")
        return redirect(url_for("assignatures.llista_assignatures"))

    # GET: Recuperem les llistes per als desplegables
    courses_list = list(mongo.db.courses.find())
    grups_list = list(mongo.db.grups.find())
    if not grups_list:
        default_grups = [{"nom": "A"}, {"nom": "B"}]
        mongo.db.grups.insert_many(default_grups)
        grups_list = list(mongo.db.grups.find())
    cicles = list(mongo.db.cicles.find())
    professors = list(mongo.db.professors.find())
    return render_template("assignatures/edit.html", assignatura=assignatura,
                           courses=courses_list, grups=grups_list, cicles=cicles, professors=professors)


@assignatures_bp.route("/delete/<id>", methods=["POST"])
@login_required
def delete_assignatura(id):
    mongo.db.assignatures.delete_one({"_id": ObjectId(id)})
    flash("Assignatura eliminada correctament.", "success")
    return redirect(url_for("assignatures.llista_assignatures"))
