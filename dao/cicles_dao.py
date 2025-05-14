from extensions import mongo
from bson.objectid import ObjectId

# Obté la llista de tots els cicles formatius
def get_all_cicles():
    return list(mongo.db.cicles.find())

# Afegeix un nou cicle amb el nom i la descripció proporcionats
def add_cicle(nom, descripcio):
    nou_cicle = {
        "nom": nom.strip(),
        "descripcio": descripcio.strip() if descripcio else ""
    }
    return mongo.db.cicles.insert_one(nou_cicle)

# Retorna un cicle a partir del seu identificador únic
def get_cicle_by_id(cicle_id):
    try:
        return mongo.db.cicles.find_one({"_id": ObjectId(cicle_id)})
    except Exception:
        return None

# Actualitza les dades d’un cicle concret
def update_cicle(cicle_id, nom, descripcio):
    try:
        return mongo.db.cicles.update_one(
            {"_id": ObjectId(cicle_id)},
            {"$set": {
                "nom": nom.strip(),
                "descripcio": descripcio.strip() if descripcio else ""
            }}
        )
    except Exception:
        return None

# Elimina un cicle de la base de dades a partir del seu identificador
def delete_cicle(cicle_id):
    try:
        return mongo.db.cicles.delete_one({"_id": ObjectId(cicle_id)})
    except Exception:
        return None
