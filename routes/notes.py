import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
from bson.objectid import ObjectId
from weasyprint import HTML, CSS
from datetime import datetime
import io

from extensions import login_required
from dao.notes_dao import *
from dao.professors_dao import get_professor_by_id
from dao.assignatures_dao import get_assignatura_by_id

notes_bp = Blueprint("notes", __name__)

# --- Validació de nom i cognoms (només lletres i espais) ---
def validar_nom_cognoms(valor):
    return bool(re.match(r"^[A-Za-zÀ-ÿ\s]+$", valor))

# --- Funció auxiliar per validar nota i camps obligatoris ---
def validar_nota_i_camps(form, ruta_error):
    alumne_id = form.get("alumne_id")
    assignatura_id = form.get("assignatura_id")
    ra_id = form.get("ra_id")
    nota_str = form.get("nota")

    if not all([alumne_id, assignatura_id, ra_id]) or nota_str is None or nota_str.strip() == "":
        flash("Tots els camps són obligatoris.", "error")
        return redirect(url_for(ruta_error)), None, None, None, None

    try:
        nota = float(nota_str)
    except ValueError:
        flash("La nota ha de ser un número.", "error")
        return redirect(url_for(ruta_error)), None, None, None, None

    return None, alumne_id, assignatura_id, ra_id, nota

# --- Llistar totes les notes (amb cerca per nom d'alumne) ---
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

# --- Afegir nova nota ---
@notes_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_nota_route():
    if request.method == "POST":
        err_redirect, alumne_id, assignatura_id, ra_id, nota = validar_nota_i_camps(request.form, "notes.add_nota_route")
        if err_redirect:
            return err_redirect

        nova_nota = {
            "alumne_id": ObjectId(alumne_id),
            "assignatura_id": ObjectId(assignatura_id),
            "ra_id": ra_id,
            "nota": nota
        }
        add_nota(nova_nota)
        flash("Nota afegida correctament.", "success")
        return redirect(url_for("notes.llista_notes"))

    alumnes = list(get_all_alumnes_dict().values())
    assignatures = get_assignatures_amb_ras()
    return render_template("notes/afegir.html", alumnes=alumnes, assignatures=assignatures)

# --- Estadístiques agregades per assignatura, grup i cicle ---
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
        alumne = alumnes.get(str(nota.get("alumne_id")))
        if not alumne:
            continue

        valor = nota.get("nota")
        if valor is None:
            continue

        assignatura_stats.setdefault(assignatura_id, []).append(valor)
        grup_stats.setdefault(str(alumne.get("grup_id", "")), []).append(valor)
        cicle_stats.setdefault(str(alumne.get("cicle_id", "")), []).append(valor)

    def calcula_mitjanes(diccionari, noms):
        return [{
            "nom": noms.get(id_, "Desconegut"),
            "mitjana": round(sum(valors) / len(valors), 2) if valors else 0
        } for id_, valors in diccionari.items() if id_]

    stats = {
        "assignatures": calcula_mitjanes(assignatura_stats, assignatures),
        "grups": calcula_mitjanes(grup_stats, grups),
        "cicles": calcula_mitjanes(cicle_stats, cicles)
    }

    return render_template("notes/stats.html", stats=stats)

# --- Editar nota existent ---
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

    # Convertir ObjectId a string per plantilla
    for camp in ["_id", "alumne_id", "assignatura_id"]:
        nota[camp] = str(nota[camp])

    alumne = get_alumne_by_id(nota["alumne_id"])
    assignatura = get_assignatura_by_id(nota["assignatura_id"])

    nota["alumne_nom"] = f"{alumne['nom']} {alumne['cognoms']}" if alumne else "Alumne desconegut"
    nota["assignatura_nom"] = assignatura["nom"] if assignatura else "Assignatura desconeguda"
    nota["ra_nom"] = nota.get("ra_id", "RA desconegut")

    return render_template("notes/edit.html", nota=nota)

# --- Eliminar una nota ---
@notes_bp.route("/delete/<id>", methods=["POST"])
@login_required
def delete_nota_route(id):
    resultat = delete_nota_by_id(id)
    if resultat.deleted_count > 0:
        flash("Nota eliminada correctament.", "success")
    else:
        flash("No s'ha pogut eliminar la nota.", "error")
    return redirect(url_for("notes.llista_notes"))

# --- Generar informe HTML per un alumne ---
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

        if assignatura_id not in informe:
            informe[assignatura_id] = {
                "assignatura_nom": assignatures_dict.get(assignatura_id, {}).get("nom", "Desconeguda"),
                "notes_ra": [],
                "mitjana": None
            }
        informe[assignatura_id]["notes_ra"].append({"ra_nom": ra_nom, "nota": valor})

    # Càlcul de mitjana ponderada
    for assignatura_id, dades in informe.items():
        assignatura = assignatures_dict.get(assignatura_id, {})
        ras = assignatura.get("ras", [])
        total_pes = sum(
            next((ra.get("ponderacio", 0) for ra in ras if ra["nom"] == nota["ra_nom"]), 0)
            for nota in dades["notes_ra"]
        )
        total_ponderat = sum(
            nota["nota"] * next((ra.get("ponderacio", 0) for ra in ras if ra["nom"] == nota["ra_nom"]), 0)
            for nota in dades["notes_ra"]
        )

        dades["mitjana"] = round(total_ponderat / total_pes, 2) if total_pes > 0 else None

    data = datetime.today().strftime("%d/%m/%Y")
    return render_template("notes/informe.html", alumne=alumne, informe=informe, current_date=data, pdf=False)

# --- Generar informe PDF amb WeasyPrint ---
@notes_bp.route("/alumne/<alumne_id>/informe/pdf")
@login_required
def exportar_informe_pdf(alumne_id):
    alumne = get_alumne_by_id(alumne_id)
    if not alumne:
        flash("Alumne no trobat.", "error")
        return redirect(url_for("notes.llista_notes"))

    informe = get_informe_per_alumne(alumne_id)
    data = datetime.today().strftime("%d/%m/%Y")
    professor = get_professor_by_id(session.get("teacher_id"))

    html = render_template(
        "pdf/informe_pdf.html",
        alumne=alumne,
        informe=informe,
        current_date=data,
        professor=professor
    )

    pdf_io = io.BytesIO()
    HTML(string=html, base_url=request.host_url).write_pdf(
        pdf_io,
        stylesheets=[CSS("static/css/informe_pdf.css")]
    )
    pdf_io.seek(0)

    response = make_response(pdf_io.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=informe_{alumne["nom"]}_{alumne["cognoms"]}.pdf'

    return response
