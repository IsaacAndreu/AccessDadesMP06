from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from extensions import mongo, login_required

notes_bp = Blueprint("notes", __name__)

@notes_bp.route("/")
@login_required
def llista_notes():
    search_query = request.args.get('search', '').strip().lower()

    # Si s'ha introduït un nom/cognom per cercar
    if search_query:
        alumnes = list(mongo.db.alumnes.find({
            "$or": [
                {"nom": {"$regex": search_query, "$options": "i"}},
                {"cognoms": {"$regex": search_query, "$options": "i"}},
                {"$expr": {
                    "$regexMatch": {
                        "input": {"$concat": ["$nom", " ", "$cognoms"]},
                        "regex": search_query,
                        "options": "i"
                    }
                }}
            ]
        }))

        alumnes_ids = [a["_id"] for a in alumnes]
        notes = list(mongo.db.notes.find({"alumne_id": {"$in": alumnes_ids}}))
    else:
        notes = list(mongo.db.notes.find())

    # Sempre agafem tots els alumnes i assignatures per crear els diccionaris
    alumnes_dict = {str(a["_id"]): f'{a["nom"]} {a["cognoms"]}' for a in mongo.db.alumnes.find()}
    assignatures_dict = {str(a["_id"]): a["nom"] for a in mongo.db.assignatures.find()}

    return render_template(
        "notes/llista.html",
        notes=notes,
        alumnes_dict=alumnes_dict,
        assignatures_dict=assignatures_dict
    )
@notes_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_nota():
    if request.method == "POST":
        alumne_id = request.form.get("alumne_id")
        assignatura_id = request.form.get("assignatura_id")
        ra_nom = request.form.get("ra_id")  # Ara serà el nom del RA
        nota = request.form.get("nota")

        if not alumne_id or not assignatura_id or not ra_nom or nota == "":
            flash("Tots els camps són obligatoris.", "error")
            return redirect(url_for("notes.add_nota"))

        try:
            nota = float(nota)
        except ValueError:
            flash("La nota ha de ser un número.", "error")
            return redirect(url_for("notes.add_nota"))

        nova_nota = {
            "alumne_id": ObjectId(alumne_id),
            "assignatura_id": ObjectId(assignatura_id),
            "ra_id": ra_nom,
            "nota": nota
        }
        mongo.db.notes.insert_one(nova_nota)
        flash("Nota afegida correctament.", "success")
        return redirect(url_for("notes.llista_notes"))

    alumnes = list(mongo.db.alumnes.find())

    # 🔁 Assignatures amb RAs dins
    assignatures_raw = list(mongo.db.assignatures.find())
    assignatures = []
    for a in assignatures_raw:
        assignatures.append({
            "_id": str(a["_id"]),
            "nom": a["nom"],
            "ras": [{"nom": ra["nom"], "ponderacio": ra.get("ponderacio", 0)} for ra in a.get("ras", [])]
        })

    return render_template("notes/add.html", alumnes=alumnes, assignatures=assignatures)

@notes_bp.route("/stats")
@login_required
def estadistiques_notes():
    notes = list(mongo.db.notes.find())
    assignatures = {str(a["_id"]): a["nom"] for a in mongo.db.assignatures.find()}
    grups = {str(g["_id"]): g["nom"] for g in mongo.db.grups.find()}
    cicles = {str(c["_id"]): c["nom"] for c in mongo.db.cicles.find()}
    alumnes = {str(a["_id"]): a for a in mongo.db.alumnes.find()}

    assignatura_stats = {}
    grup_stats = {}
    cicle_stats = {}

    for nota in notes:
        assignatura_id = str(nota.get("assignatura_id"))
        alumne_id = str(nota.get("alumne_id"))

        alumne = alumnes.get(alumne_id)
        if not alumne:
            continue

        grup_id = str(alumne.get("grup_id", ""))
        cicle_id = str(alumne.get("cicle_id", ""))

        valor = nota.get("nota")
        if valor is None:
            continue

        if assignatura_id not in assignatura_stats:
            assignatura_stats[assignatura_id] = []
        assignatura_stats[assignatura_id].append(valor)

        if grup_id:
            if grup_id not in grup_stats:
                grup_stats[grup_id] = []
            grup_stats[grup_id].append(valor)

        if cicle_id:
            if cicle_id not in cicle_stats:
                cicle_stats[cicle_id] = []
            cicle_stats[cicle_id].append(valor)

    def calcula_mitjanes(diccionari, noms):
        resultats = []
        for id_, valors in diccionari.items():
            mitjana = round(sum(valors) / len(valors), 2) if valors else 0
            resultats.append({
                "nom": noms.get(id_, "Desconegut"),
                "mitjana": mitjana
            })
        return resultats

    stats = {
        "assignatures": calcula_mitjanes(assignatura_stats, assignatures),
        "grups": calcula_mitjanes(grup_stats, grups),
        "cicles": calcula_mitjanes(cicle_stats, cicles)
    }

    return render_template("notes/stats.html", stats=stats)
@notes_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_nota(id):
    nota = mongo.db.notes.find_one({"_id": ObjectId(id)})
    if not nota:
        flash("Nota no trobada.", "error")
        return redirect(url_for("notes.llista_notes"))

    if request.method == "POST":
        nou_valor = request.form.get("nota")
        nou_ra = request.form.get("ra_id")

        try:
            nota_float = float(nou_valor)
        except ValueError:
            flash("La nota ha de ser un número.", "error")
            return redirect(url_for("notes.edit_nota", id=id))

        mongo.db.notes.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "nota": nota_float,
                "ra_id": nou_ra
            }}
        )
        flash("Nota actualitzada correctament.", "success")
        return redirect(url_for("notes.llista_notes"))

    # Carreguem assignatures amb RAs per mostrar al desplegable
    assignatures_raw = list(mongo.db.assignatures.find())
    assignatures = []
    for a in assignatures_raw:
        assignatures.append({
            "_id": str(a["_id"]),
            "nom": a["nom"],
            "ras": [{"nom": ra["nom"], "ponderacio": ra.get("ponderacio", 0)} for ra in a.get("ras", [])]
        })

    # Convertim IDs per passar al template
    nota["_id"] = str(nota["_id"])
    nota["alumne_id"] = str(nota["alumne_id"])
    nota["assignatura_id"] = str(nota["assignatura_id"])

    return render_template("notes/edit.html", nota=nota, assignatures=assignatures)
@notes_bp.route("/delete/<id>", methods=["POST"])
@login_required
def delete_nota(id):
    resultat = mongo.db.notes.delete_one({"_id": ObjectId(id)})

    if resultat.deleted_count > 0:
        flash("Nota eliminada correctament.", "success")
    else:
        flash("No s'ha pogut eliminar la nota.", "error")

    return redirect(url_for("notes.llista_notes"))
@notes_bp.route("/informe/<alumne_id>")
@login_required
def informe_alumne(alumne_id):
    alumne = mongo.db.alumnes.find_one({"_id": ObjectId(alumne_id)})
    if not alumne:
        flash("Alumne no trobat.", "error")
        return redirect(url_for("notes.llista_notes"))

    notes = list(mongo.db.notes.find({"alumne_id": ObjectId(alumne_id)}))
    assignatures_dict = {str(a["_id"]): a for a in mongo.db.assignatures.find()}

    informe = {}

    for nota in notes:
        assignatura_id = str(nota["assignatura_id"])
        ra_nom = nota["ra_id"]
        valor = nota["nota"]

        if assignatura_id not in informe:
            informe[assignatura_id] = {
                "assignatura_nom": assignatures_dict.get(assignatura_id, {}).get("nom", "Desconeguda"),
                "notes_ra": [],
                "mitjana": None
            }

        informe[assignatura_id]["notes_ra"].append({"ra_nom": ra_nom, "nota": valor})

    # Calcular la mitjana ponderada per assignatura
    for assignatura_id, dades in informe.items():
        assignatura = assignatures_dict.get(assignatura_id)
        ras = assignatura.get("ras", []) if assignatura else []
        total_pes = 0
        total_ponderat = 0

        for ra in dades["notes_ra"]:
            ra_info = next((r for r in ras if r["nom"] == ra["ra_nom"]), None)
            ponderacio = ra_info.get("ponderacio", 0) if ra_info else 0
            total_ponderat += ra["nota"] * ponderacio
            total_pes += ponderacio

        if total_pes > 0:
            dades["mitjana"] = round(total_ponderat / total_pes, 2)

    return render_template("notes/informe.html", alumne=alumne, informe=informe)
