from extensions import mongo
from bson.objectid import ObjectId

def get_all_notes():
    return list(mongo.db.notes.find())

def get_notes_by_alumnes_ids(alumnes_ids):
    return list(mongo.db.notes.find({"alumne_id": {"$in": alumnes_ids}}))

def get_alumnes_dict():
    return {str(a["_id"]): f'{a["nom"]} {a["cognoms"]}' for a in mongo.db.alumnes.find()}

def get_assignatures_dict():
    return {str(a["_id"]): a["nom"] for a in mongo.db.assignatures.find()}

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

def add_nota(nova_nota):
    return mongo.db.notes.insert_one(nova_nota)

def get_assignatures_amb_ras():
    assignatures_raw = list(mongo.db.assignatures.find())
    assignatures = []
    for a in assignatures_raw:
        assignatures.append({
            "_id": str(a["_id"]),
            "nom": a["nom"],
            "ras": [{"nom": ra["nom"], "ponderacio": ra.get("ponderacio", 0)} for ra in a.get("ras", [])]
        })
    return assignatures

def get_all_assignatures_raw():
    return list(mongo.db.assignatures.find())

def get_all_grups_dict():
    return {str(g["_id"]): g["nom"] for g in mongo.db.grups.find()}

def get_all_cicles_dict():
    return {str(c["_id"]): c["nom"] for c in mongo.db.cicles.find()}

def get_all_alumnes_dict():
    return {str(a["_id"]): a for a in mongo.db.alumnes.find()}

def get_nota_by_id(nota_id):
    return mongo.db.notes.find_one({"_id": ObjectId(nota_id)})

def update_nota(nota_id, nota_float, nou_ra):
    return mongo.db.notes.update_one(
        {"_id": ObjectId(nota_id)},
        {"$set": {
            "nota": nota_float,
            "ra_id": nou_ra
        }}
    )

def delete_nota_by_id(nota_id):
    return mongo.db.notes.delete_one({"_id": ObjectId(nota_id)})

def get_notes_by_alumne(alumne_id):
    return list(mongo.db.notes.find({"alumne_id": ObjectId(alumne_id)}))

def get_alumne_by_id(alumne_id):
    return mongo.db.alumnes.find_one({"_id": ObjectId(alumne_id)})
