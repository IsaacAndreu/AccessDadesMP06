from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from extensions import login_required, mongo

alumnes_bp = Blueprint("alumnes", __name__)


@alumnes_bp.route("/", methods=["GET"])
@login_required
def llista_alumnesa():
    # 1. Obtenim els paràmetres GET si existeixen
    grup_id = request.args.get("grup_id", "")     # Exemple: "63bd4..." (ObjectId en string) o "A" si emmagatzemes directament el nom
    cicle_id = request.args.get("cicle_id", "")   # Exemple: "63bd8..."

    # 2. Muntem el filtre
    filtre = {}
    if grup_id:
        # Ajusta segons com guardis el 'grup' als alumnes:
        # Si el camp "grup" és un ObjectId, fem:
        #   filtre["grup"] = ObjectId(grup_id)
        # Si el camp "grup" és directament el nom (A/B/...), fem:
        filtre["grup"] = grup_id

    if cicle_id:
        # Si 'cicle_id' s'emmagatzema com un ObjectId a l'alumne, fem:
        filtre["cicle_id"] = ObjectId(cicle_id)

    # 3. Recuperem els alumnes filtrats
    alumnes = list(mongo.db.alumnes.find(filtre))

    # Recuperem els grups per mostrar el seu nom en lloc de l'ID
    grups = list(mongo.db.grups.find())
    grups_dict = {str(g["_id"]): g["nom"] for g in grups}

    # Recuperem els cicles per mostrar el seu nom en lloc de l'ID
    cicles = list(mongo.db.cicles.find())
    cicles_dict = {str(c["_id"]): c["nom"] for c in cicles}

    # 4. Rendertizem i passem també els valors de 'grup_id' i 'cicle_id' seleccionats
    return render_template(
        "alumnes/llista.html",
        alumnes=alumnes,
        grups=grups,
        grups_dict=grups_dict,
        cicles=cicles,
        cicles_dict=cicles_dict,
        grup_id_seleccionat=grup_id,
        cicle_id_seleccionat=cicle_id
    )


@alumnes_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_alumne():
    if request.method == "POST":
        nom = request.form.get("nom")
        cognoms = request.form.get("cognoms")
        email = request.form.get("email")
        grup = request.form.get("grup")  # Grup seleccionat (de la col·lecció grups)
        cicle_id = request.form.get("cicle_id")  # Cicle seleccionat (de la col·lecció cicles)
        curs = request.form.get("curs")  # Curs (1r, 2n, etc.)

        if not nom or not cognoms or not grup or not cicle_id or not curs:
            flash("Nom, cognoms, grup, cicle i curs són obligatoris.", "error")
            return redirect(url_for("alumnes.add_alumne"))

        mongo.db.alumnes.insert_one({
            "nom": nom.strip(),
            "cognoms": cognoms.strip(),
            "email": email.strip() if email else "",
            "grup": grup,  # Emmagatzemat com a cadena (l'ID del grup) o un ObjectId, depenent de la teva lògica
            "cicle_id": ObjectId(cicle_id),
            "curs": curs
        })
        flash("Alumne afegit correctament.", "success")
        return redirect(url_for("alumnes.llista_alumnes"))

    # GET: Recuperem grups i cicles per al formulari
    grups = list(mongo.db.grups.find())
    if not grups:
        default_grups = [{"nom": "A"}, {"nom": "B"}]
        mongo.db.grups.insert_many(default_grups)
        grups = list(mongo.db.grups.find())

    cicles = list(mongo.db.cicles.find())
    return render_template("alumnes/add.html", grups=grups, cicles=cicles)


@alumnes_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_alumne(id):
    alumne = mongo.db.alumnes.find_one({"_id": ObjectId(id)})
    if not alumne:
        flash("Alumne no trobat.", "error")
        return redirect(url_for("alumnes.llista_alumnes"))

    if request.method == "POST":
        nom = request.form.get("nom")
        cognoms = request.form.get("cognoms")
        email = request.form.get("email")
        grup = request.form.get("grup")
        cicle_id = request.form.get("cicle_id")
        curs = request.form.get("curs")

        if not nom or not cognoms or not grup or not cicle_id or not curs:
            flash("Nom, cognoms, grup, cicle i curs són obligatoris.", "error")
            return redirect(url_for("alumnes.edit_alumne", id=id))

        mongo.db.alumnes.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "nom": nom.strip(),
                "cognoms": cognoms.strip(),
                "email": email.strip() if email else "",
                "grup": grup,
                "cicle_id": ObjectId(cicle_id),
                "curs": curs
            }}
        )
        flash("Alumne actualitzat correctament.", "success")
        return redirect(url_for("alumnes.llista_alumnes"))

    # GET: Recuperem grups i cicles per el desplegable
    grups = list(mongo.db.grups.find())
    if not grups:
        default_grups = [{"nom": "A"}, {"nom": "B"}]
        mongo.db.grups.insert_many(default_grups)
        grups = list(mongo.db.grups.find())

    cicles = list(mongo.db.cicles.find())
    return render_template("alumnes/edit.html", alumne=alumne, grups=grups, cicles=cicles)


@alumnes_bp.route("/delete/<id>", methods=["POST"])
@login_required
def delete_alumne(id):
    mongo.db.alumnes.delete_one({"_id": ObjectId(id)})
    flash("Alumne eliminat correctament.")
    return redirect(url_for("alumnes.llista_alumnes"))
