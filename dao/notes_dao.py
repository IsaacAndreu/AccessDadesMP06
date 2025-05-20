from extensions import mongo
from bson.objectid import ObjectId
from dao.db_selector import get_db_connection, ORACLE

# Obté totes les notes registrades
def get_all_notes():
    return list(mongo.db.notes.find())

# Obté les notes de diversos alumnes a partir dels seus IDs
def get_notes_by_alumnes_ids(alumnes_ids):
    return list(mongo.db.notes.find({"alumne_id": {"$in": alumnes_ids}}))

# Retorna un diccionari amb els alumnes: {id: nom complet}
def get_alumnes_dict():
    """
    Retorna un diccionari amb id (com a string) → nom complet
    Funciona tant amb Mongo (_id) com amb Oracle (id enter).
    """
    try:
        from dao.oracle_alumnes_dao import get_alumnes_filtrats
        alumnes = get_alumnes_filtrats(None, None)
        return {str(a.id): f"{a.nom} {a.cognoms}" for a in alumnes}
    except ImportError:
        return {str(a["_id"]): f'{a["nom"]} {a["cognoms"]}' for a in mongo.db.alumnes.find()}

# Diccionari amb les assignatures: {id: nom}
def get_assignatures_dict():
    return {str(a["_id"]): a["nom"] for a in mongo.db.assignatures.find()}

# Cerca alumnes per nom, cognom o nom complet
def get_alumnes_by_nom(search_query):
    return list(mongo.db.alumnes.find({
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

# Afegeix una nova nota a la base de dades
def add_nota(nova_nota):
    return mongo.db.notes.insert_one(nova_nota)

# Retorna assignatures amb els seus RAs (per select)
def get_assignatures_amb_ras():
    assignatures_raw = mongo.db.assignatures.find()
    return [{
        "_id": str(a["_id"]),
        "nom": a["nom"],
        "ras": [{"nom": ra["nom"], "ponderacio": ra.get("ponderacio", 0)} for ra in a.get("ras", [])]
    } for a in assignatures_raw]

# Llista completa d’assignatures (en format RAW)
def get_all_assignatures_raw():
    return list(mongo.db.assignatures.find())

# Diccionari de tots els grups
def get_all_grups_dict():
    return {str(g["_id"]): g["nom"] for g in mongo.db.grups.find()}

# Diccionari de tots els cicles
def get_all_cicles_dict():
    return {str(c["_id"]): c["nom"] for c in mongo.db.cicles.find()}

# Diccionari amb tots els alumnes complets (per ús intern)
def get_all_alumnes_dict():
    return {str(a["_id"]): a for a in mongo.db.alumnes.find()}

# Obté una nota concreta pel seu ID
def get_nota_by_id(nota_id):
    return mongo.db.notes.find_one({"_id": ObjectId(nota_id)})

# Actualitza una nota i el seu RA associat
def update_nota(nota_id, nota_float, nou_ra):
    return mongo.db.notes.update_one(
        {"_id": ObjectId(nota_id)},
        {"$set": {
            "nota": nota_float,
            "ra_id": nou_ra
        }}
    )

# Elimina una nota per identificador
def delete_nota_by_id(nota_id):
    return mongo.db.notes.delete_one({"_id": ObjectId(nota_id)})

# Obté totes les notes d’un alumne específic
# Obté totes les notes d’un alumne específic (ID numèric)
def get_notes_by_alumne(alumne_id):
    """
    Retorna totes les notes d’un alumne identificat pel seu ID numèric.
    """
    try:
        student_id = int(alumne_id)
    except (TypeError, ValueError):
        raise ValueError(f"Alumne_id ha de ser un enter vàlid, s’ha passat: {alumne_id!r}")
    return list(mongo.db.notes.find({"alumne_id": student_id}))

# Retorna les dades d’un alumne pel seu ID
def get_alumne_by_id(alumne_id):
    return mongo.db.alumnes.find_one({"_id": ObjectId(alumne_id)})

# Construeix l'informe d’un alumne amb ponderacions per RA
def get_informe_per_alumne(alumne_id):
    notes = get_notes_by_alumne(alumne_id)
    assignatures_dict = {str(a["_id"]): a for a in get_all_assignatures_raw()}
    informe = {}

    for nota in notes:
        assignatura_id = str(nota["assignatura_id"])
        ra_nom = nota["ra_id"]
        valor = nota["nota"]

        dades_assignatura = informe.setdefault(assignatura_id, {
            "assignatura_nom": assignatures_dict.get(assignatura_id, {}).get("nom", "Desconeguda"),
            "notes_ra": [],
            "mitjana": None
        })
        dades_assignatura["notes_ra"].append({"ra_nom": ra_nom, "nota": valor})

    for assignatura_id, dades in informe.items():
        assignatura = assignatures_dict.get(assignatura_id)
        ras = assignatura.get("ras", []) if assignatura else []

        total_pes = sum(
            next((ra.get("ponderacio", 0) for ra in ras if ra["nom"] == nota["ra_nom"]), 0)
            for nota in dades["notes_ra"]
        )
        total_ponderat = sum(
            nota["nota"] * next((ra.get("ponderacio", 0) for ra in ras if ra["nom"] == nota["ra_nom"]), 0)
            for nota in dades["notes_ra"]
        )

        if total_pes > 0:
            dades["mitjana"] = round(total_ponderat / total_pes, 2)

    return informe
