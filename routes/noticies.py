from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import login_required, admin_required
from dao.noticies_dao import (
    get_all_noticies,
    get_noticia_by_id,
    editar_noticia,
    eliminar_noticia,
    afegir_noticia as guardar_noticia
)
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import re

noticies_bp = Blueprint("noticies", __name__, url_prefix="/noticies")


def validar_text_simple(valor):
    """Validar que el text només contingui lletres (incloent accents) i espais."""
    return bool(re.match(r"^[A-Za-zÀ-ÿ\s]+$", valor))


def guardar_imatge(imatge):
    """Guarda la imatge i retorna el nom segur del fitxer o None si no hi ha imatge."""
    if imatge and imatge.filename:
        nom_imatge = secure_filename(imatge.filename)
        ruta_guardat = os.path.join("static/uploads/noticies", nom_imatge)
        imatge.save(ruta_guardat)
        return nom_imatge
    return None


@noticies_bp.route("/")
@login_required
def llistar_noticies():
    noticies = get_all_noticies()
    return render_template("noticies/llista.html", noticies=noticies)


@noticies_bp.route("/afegir", methods=["GET", "POST"])
@login_required
@admin_required
def formulari_afegir_noticia():
    if request.method == "POST":
        titol = request.form.get("titol", "").strip()
        cos = request.form.get("cos", "").strip()
        imatge = request.files.get("imatge")

        if not titol or not cos:
            flash("Tots els camps són obligatoris.", "error")
            return redirect(url_for("noticies.formulari_afegir_noticia"))

        if not (validar_text_simple(titol) and validar_text_simple(cos)):
            flash("Nom o cos contenen caràcters no vàlids. Només es permeten lletres i espais.", "error")
            return redirect(url_for("noticies.formulari_afegir_noticia"))

        nom_imatge = guardar_imatge(imatge)
        nova = {
            "titol": titol,
            "cos": cos,
            "autor": session.get("professor_nom", "Anònim"),
            "data": datetime.now(),
            "imatge": nom_imatge
        }
        guardar_noticia(nova)
        flash("Notícia afegida!", "success")
        return redirect(url_for("noticies.llistar_noticies"))

    return render_template("noticies/afegir.html")


@noticies_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
@admin_required
def editar_noticia_route(id):
    noticia = get_noticia_by_id(id)
    if not noticia:
        flash("Notícia no trobada.", "error")
        return redirect(url_for("noticies.llistar_noticies"))

    if request.method == "POST":
        titol = request.form.get("titol", "").strip()
        cos = request.form.get("cos", "").strip()
        imatge = request.files.get("imatge")

        if not titol or not cos:
            flash("Tots els camps són obligatoris.", "error")
            return redirect(url_for("noticies.editar_noticia_route", id=id))

        if not (validar_text_simple(titol) and validar_text_simple(cos)):
            flash("Nom o cos contenen caràcters no vàlids. Només es permeten lletres i espais.", "error")
            return redirect(url_for("noticies.editar_noticia_route", id=id))

        nom_imatge = noticia.get("imatge")
        nova_imatge = guardar_imatge(imatge)
        if nova_imatge:
            nom_imatge = nova_imatge

        noves_dades = {
            "titol": titol,
            "cos": cos,
            "imatge": nom_imatge
        }

        editar_noticia(id, noves_dades)
        flash("Notícia actualitzada correctament.", "success")
        return redirect(url_for("noticies.llistar_noticies"))

    return render_template("noticies/edit.html", noticia=noticia)


@noticies_bp.route("/delete/<id>", methods=["POST"])
@login_required
@admin_required
def eliminar_noticia_route(id):
    eliminar_noticia(id)
    flash("Notícia eliminada.", "success")
    return redirect(url_for("noticies.llistar_noticies"))


@noticies_bp.route("/<id>")
@login_required
def veure_noticia(id):
    noticia = get_noticia_by_id(id)
    if not noticia:
        flash("Notícia no trobada.", "error")
        return redirect(url_for("noticies.llistar_noticies"))
    return render_template("noticies/detall.html", noticia=noticia)
