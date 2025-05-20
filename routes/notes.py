# routes/notes.py

import json
import re
import io
from datetime import datetime
from bson import ObjectId
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from weasyprint import HTML, CSS

from extensions import login_required
from dao.db_selector import get_db_connection, ORACLE
from dao.notes_dao import (
    add_nota,
    get_all_notes,
    get_nota_by_id,
    update_nota,
    delete_nota_by_id,
    get_informe_per_alumne,
    get_all_assignatures_raw,
    get_assignatures_dict
)
from dao.assignatures_dao import get_assignatures_amb_ras, get_assignatura_by_id
from dao.oracle_alumnes_dao import get_alumnes_filtrats, get_alumne_by_id

notes_bp = Blueprint("notes", __name__, url_prefix="/notes")

def oid_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, dict):
        return {k: oid_to_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [oid_to_str(v) for v in obj]
    return obj

def validar_nota_i_camps(form, ruta_error):
    alumne_id = form.get("alumne_id")
    assignatura_id = form.get("assignatura_id")
    ra_id = form.get("ra_id")
    nota_str = form.get("nota")
    if not all([alumne_id, assignatura_id, ra_id]) or not nota_str:
        flash("Tots els camps són obligatoris.", "error")
        return redirect(url_for(ruta_error)), None, None, None, None
    try:
        nota = float(nota_str)
    except ValueError:
        flash("La nota ha de ser un número.", "error")
        return redirect(url_for(ruta_error)), None, None, None, None
    return None, alumne_id, assignatura_id, ra_id, nota


@notes_bp.route("/", methods=["GET"])
@login_required
def llista_notes():
    # 1) carrega totes les notes de Mongo
    notes = get_all_notes()
    # 2) converteix ids a str
    for n in notes:
        n["alumne_id"]      = str(n["alumne_id"])
        n["assignatura_id"] = str(n["assignatura_id"])
    # 3) filtra si ve search
    search_id = request.args.get("search", "").strip()
    if search_id:
        notes = [n for n in notes if n["alumne_id"] == search_id]
    # 4) diccionari alumnes Oracle
    alumnes = get_alumnes_filtrats(None, None)
    alumnes_dict = { str(a.id): f"{a.nom} {a.cognoms}" for a in alumnes }
    # 5) diccionari assignatures Mongo
    assignatures_dict = get_assignatures_dict()

    return render_template(
        "notes/llista.html",
        notes=notes,
        alumnes_dict=alumnes_dict,
        assignatures_dict=assignatures_dict,
        search_id=search_id
    )


@notes_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_nota_route():
    if request.method == "POST":
        err, alumne_id, assignatura_id, ra_id, nota = validar_nota_i_camps(request.form, "notes.add_nota_route")
        if err:
            return err
        doc = {
            "alumne_id": int(alumne_id),
            "assignatura_id": ObjectId(assignatura_id),
            "ra_id": ra_id,
            "nota": nota
        }
        add_nota(doc)
        flash("Nota afegida correctament.", "success")
        return redirect(url_for("notes.llista_notes"))

    alumnes = get_alumnes_filtrats(None, None)
    raw_as   = get_assignatures_amb_ras()
    safe_as  = oid_to_str(raw_as)
    assignatures_json = json.dumps(safe_as)

    return render_template(
        "notes/afegir.html",
        alumnes=alumnes,
        assignatures_json=assignatures_json
    )


@notes_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_nota(id):
    nota = get_nota_by_id(id)
    if not nota:
        flash("Nota no trobada.", "error")
        return redirect(url_for("notes.llista_notes"))
    if request.method == "POST":
        nou_valor = request.form.get("nota")
        nou_ra    = request.form.get("ra_id")
        try:
            nota_float = float(nou_valor)
        except ValueError:
            flash("La nota ha de ser un número.", "error")
            return redirect(url_for("notes.edit_nota", id=id))
        update_nota(id, nota_float, nou_ra)
        flash("Nota actualitzada correctament.", "success")
        return redirect(url_for("notes.llista_notes"))

    for camp in ["_id", "alumne_id", "assignatura_id"]:
        nota[camp] = str(nota[camp])

    alumne     = get_alumne_by_id(int(nota["alumne_id"]))
    assignatura= get_assignatura_by_id(nota["assignatura_id"])

    nota["alumne_nom"]      = f"{alumne.nom} {alumne.cognoms}" if alumne else "Alumne desconegut"
    nota["assignatura_nom"] = assignatura.nom if assignatura else "Assignatura desconeguda"
    nota["ra_nom"]          = nota.get("ra_id", "RA desconegut")

    return render_template("notes/edit.html", nota=nota)


@notes_bp.route("/delete/<id>", methods=["POST"])
@login_required
def delete_nota_route(id):
    resultat = delete_nota_by_id(id)
    flash(
      "Nota eliminada correctament." if resultat.deleted_count else "No s'ha pogut eliminar la nota.",
      "success" if resultat.deleted_count else "error"
    )
    return redirect(url_for("notes.llista_notes"))


@notes_bp.route("/informe/<alumne_id>")
@login_required
def informe_alumne(alumne_id):
    alumne = get_alumne_by_id(int(alumne_id))
    if not alumne:
        flash("Alumne no trobat.", "error")
        return redirect(url_for("notes.llista_notes"))

    # Recull i filtra notes:
    notes = [n for n in get_all_notes() if n.get("alumne_id")==int(alumne_id)]
    # Construeix informe igual que get_informe_per_alumne
    raw_as = get_all_assignatures_raw()
    assignatures_dict = { str(a["_id"]): a for a in raw_as }
    informe = {}
    for n in notes:
        aid = str(n["assignatura_id"])
        ra_nom = n["ra_id"]
        val = n["nota"]
        if aid not in informe:
            informe[aid] = {
                "assignatura_nom": assignatures_dict.get(aid,{}).get("nom","Desconeguda"),
                "notes_ra": [], "mitjana": None
            }
        informe[aid]["notes_ra"].append({"ra_nom": ra_nom, "nota": val})
    # Calcula mitjana ponderada
    for aid, dades in informe.items():
        ras = assignatures_dict.get(aid,{}).get("ras",[])
        total_pes = sum(next((r["ponderacio"] for r in ras if r["nom"]==x["ra_nom"]),0) for x in dades["notes_ra"])
        total_pond= sum(x["nota"]*next((r["ponderacio"] for r in ras if r["nom"]==x["ra_nom"]),0) for x in dades["notes_ra"])
        dades["mitjana"] = round(total_pond/total_pes,2) if total_pes else None

    return render_template(
        "notes/informe.html",
        alumne=alumne,
        informe=informe,
        current_date=datetime.today().strftime("%d/%m/%Y"),
        pdf=False
    )


@notes_bp.route("/alumne/<alumne_id>/informe/pdf")
@login_required
def exportar_informe_pdf(alumne_id):
    # Repeteix lògica de informe_alumne però escriu PDF
    alumne = get_alumne_by_id(int(alumne_id))
    html = render_template(
        "pdf/informe_pdf.html",
        alumne=alumne,
        informe=get_informe_per_alumne(alumne_id),
        current_date=datetime.today().strftime("%d/%m/%Y"),
        pdf=True
    )

    pdf_io = io.BytesIO()
    HTML(string=html, base_url=request.host_url).write_pdf(
        pdf_io,
        stylesheets=[CSS("static/css/informe_pdf.css")]
    )
    pdf_io.seek(0)

    resp = make_response(pdf_io.read())
    resp.headers.update({
        "Content-Type": "application/pdf",
        "Content-Disposition": (
            f'inline; filename="informe_{alumne.nom}_{alumne.cognoms}.pdf"'
        )
    })
    return resp
