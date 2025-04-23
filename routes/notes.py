from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from extensions import login_required
from dao.notes_dao import *  # Si tens les funcions dins del fitxer

notes_bp = Blueprint("notes", __name__)

@notes_bp.route("/")
@login_required
def llista_notes():
    search_query = request.args.get('search', '').strip().lower()

    if search_query:
        alumnes = get_alumnes_by_nom(search_query)
        alumnes_ids = [a["_id"] for a in alumnes]
        notes = get_notes_by_alumnes_ids(alumnes_ids)
    else:
        notes = get_all_notes()

    alumnes_dict = get_alumnes_dict()
    assignatures_dict = get_assignatures_dict()

    return render_template("notes/llista.html", notes=notes, alumnes_dict=alumnes_dict, assignatures_dict=assignatures_dict)


@notes_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_nota():
    if request.method == "POST":
        alumne_id = request.form.get("alumne_id")
        assignatura_id = request.form.get("assignatura_id")
        ra_nom = request.form.get("ra_id")
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
        add_nota(nova_nota)
        flash("Nota afegida correctament.", "success")
        return redirect(url_for("notes.llista_notes"))

    alumnes = list(get_all_alumnes_dict().values())
    assignatures = get_assignatures_amb_ras()
    return render_template("notes/add.html", alumnes=alumnes, assignatures=assignatures)


@notes_bp.route("/stats")
@login_required
def estadistiques_notes():
    notes = get_all_notes()
    assignatures = get_assignatures_dict()
    grups = get_all_grups_dict()
    cicles = get_all_cicles_dict()
    alumnes = get_all_alumnes_dict()

    assignatura_stats, grup_stats, cicle_stats = {}, {}, {}

    for nota in notes:
        assignatura_id = str(nota.get("assignatura_id"))
        alumne_id = str(nota.get("alumne_id"))
        alumne = alumnes.get(alumne_id)
        if not alumne: continue

        grup_id = str(alumne.get("grup_id", ""))
        cicle_id = str(alumne.get("cicle_id", ""))
        valor = nota.get("nota")
        if valor is None: continue

        assignatura_stats.setdefault(assignatura_id, []).append(valor)
        if grup_id:
            grup_stats.setdefault(grup_id, []).append(valor)
        if cicle_id:
            cicle_stats.setdefault(cicle_id, []).append(valor)

    def calcula_mitjanes(diccionari, noms):
        return [{
            "nom": noms.get(id_, "Desconegut"),
            "mitjana": round(sum(valors) / len(valors), 2) if valors else 0
        } for id_, valors in diccionari.items()]

    stats = {
        "assignatures": calcula_mitjanes(assignatura_stats, assignatures),
        "grups": calcula_mitjanes(grup_stats, grups),
        "cicles": calcula_mitjanes(cicle_stats, cicles)
    }

    return render_template("notes/stats.html", stats=stats)


@notes_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_nota(id):
    nota = get_nota_by_id(id)
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

        update_nota(id, nota_float, nou_ra)
        flash("Nota actualitzada correctament.", "success")
        return redirect(url_for("notes.llista_notes"))

    assignatures = get_assignatures_amb_ras()
    nota["_id"] = str(nota["_id"])
    nota["alumne_id"] = str(nota["alumne_id"])
    nota["assignatura_id"] = str(nota["assignatura_id"])

    return render_template("notes/edit.html", nota=nota, assignatures=assignatures)


@notes_bp.route("/delete/<id>", methods=["POST"])
@login_required
def delete_nota_route(id):
    resultat = delete_nota_by_id(id)
    if resultat.deleted_count > 0:
        flash("Nota eliminada correctament.", "success")
    else:
        flash("No s'ha pogut eliminar la nota.", "error")
    return redirect(url_for("notes.llista_notes"))


@notes_bp.route("/informe/<alumne_id>")
@login_required
def informe_alumne(alumne_id):
    alumne = get_alumne_by_id(alumne_id)
    if not alumne:
        flash("Alumne no trobat.", "error")
        return redirect(url_for("notes.llista_notes"))

    notes = get_notes_by_alumne(alumne_id)
    assignatures_dict = {str(a["_id"]): a for a in get_all_assignatures_raw()}

    informe = {}
    for nota in notes:
        assignatura_id = str(nota["assignatura_id"])
        ra_nom = nota["ra_id"]
        valor = nota["nota"]
        informe.setdefault(assignatura_id, {
            "assignatura_nom": assignatures_dict.get(assignatura_id, {}).get("nom", "Desconeguda"),
            "notes_ra": [],
            "mitjana": None
        })["notes_ra"].append({"ra_nom": ra_nom, "nota": valor})

    for assignatura_id, dades in informe.items():
        assignatura = assignatures_dict.get(assignatura_id)
        ras = assignatura.get("ras", []) if assignatura else []
        total_pes = sum([next((ra.get("ponderacio", 0) for ra in ras if ra["nom"] == nota["ra_nom"]), 0)
                         for nota in dades["notes_ra"]])
        total_ponderat = sum([nota["nota"] * next((ra.get("ponderacio", 0)
                               for ra in ras if ra["nom"] == nota["ra_nom"]), 0)
                               for nota in dades["notes_ra"]])

        if total_pes > 0:
            dades["mitjana"] = round(total_ponderat / total_pes, 2)

    return render_template("notes/informe.html", alumne=alumne, informe=informe)
