from extensions import mongo
from bson.objectid import ObjectId

def get_alumnes_filtrats(grup_id=None, cicle_id=None):
    filtre = {}
    if grup_id:
        filtre["grup"] = grup_id  # Ajusta si guardes grup com a ObjectId
    if cicle_id:
        filtre["cicle_id"] = ObjectId(cicle_id)
    return list(mongo.db.alumnes.find(filtre))

def get_grups():
    grups = list(mongo.db.grups.find())
    if not grups:
        mongo.db.grups.insert_many([{"nom": "A"}, {"nom": "B"}])
        grups = list(mongo.db.grups.find())
    return grups

def get_cicles():
    return list(mongo.db.cicles.find())

def add_alumne(nom, cognoms, email, grup, cicle_id, curs):
    return mongo.db.alumnes.insert_one({
        "nom": nom.strip(),
        "cognoms": cognoms.strip(),
        "email": email.strip() if email else "",
        "grup": grup,
        "cicle_id": ObjectId(cicle_id),
        "curs": curs
    })

def get_alumne_by_id(alumne_id):
    return mongo.db.alumnes.find_one({"_id": ObjectId(alumne_id)})

def update_alumne(alumne_id, nom, cognoms, email, grup, cicle_id, curs):
    return mongo.db.alumnes.update_one(
        {"_id": ObjectId(alumne_id)},
        {"$set": {
            "nom": nom.strip(),
            "cognoms": cognoms.strip(),
            "email": email.strip() if email else "",
            "grup": grup,
            "cicle_id": ObjectId(cicle_id),
            "curs": curs
        }}
    )

def delete_alumne_by_id(alumne_id):
    return mongo.db.alumnes.delete_one({"_id": ObjectId(alumne_id)})
