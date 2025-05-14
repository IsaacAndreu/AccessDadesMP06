from extensions import mongo
from bson.objectid import ObjectId

# Retorna tots els grups disponibles a la base de dades
def get_all_grups():
    return list(mongo.db.grups.find())

# Afegeix un nou grup amb el nom proporcionat
def add_grup(nom):
    return mongo.db.grups.insert_one({
        "nom": nom.strip()
    })

# Retorna un grup pel seu identificador únic
def get_grup_by_id(grup_id):
    try:
        return mongo.db.grups.find_one({"_id": ObjectId(grup_id)})
    except Exception:
        return None

# Actualitza el nom d’un grup existent
def update_grup(grup_id, nom):
    try:
        return mongo.db.grups.update_one(
            {"_id": ObjectId(grup_id)},
            {"$set": {"nom": nom.strip()}}
        )
    except Exception:
        return None

# Elimina un grup segons el seu identificador
def delete_grup(grup_id):
    try:
        return mongo.db.grups.delete_one({"_id": ObjectId(grup_id)})
    except Exception:
        return None
