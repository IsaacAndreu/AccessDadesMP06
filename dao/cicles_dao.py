from extensions import mongo
from bson.objectid import ObjectId

def get_all_cicles():
    return list(mongo.db.cicles.find())

def add_cicle(nom, descripcio):
    nou_cicle = {
        "nom": nom.strip(),
        "descripcio": descripcio.strip() if descripcio else ""
    }
    return mongo.db.cicles.insert_one(nou_cicle)

def get_cicle_by_id(cicle_id):
    return mongo.db.cicles.find_one({"_id": ObjectId(cicle_id)})

def update_cicle(cicle_id, nom, descripcio):
    return mongo.db.cicles.update_one(
        {"_id": ObjectId(cicle_id)},
        {"$set": {
            "nom": nom.strip(),
            "descripcio": descripcio.strip() if descripcio else ""
        }}
    )

def delete_cicle(cicle_id):
    return mongo.db.cicles.delete_one({"_id": ObjectId(cicle_id)})
