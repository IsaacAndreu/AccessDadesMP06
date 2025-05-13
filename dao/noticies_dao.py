from extensions import mongo
from bson.objectid import ObjectId

def get_all_noticies():
    return list(mongo.db.noticies.find().sort("data", -1))

def get_noticia_by_id(id):
    return mongo.db.noticies.find_one({"_id": ObjectId(id)})

def afegir_noticia(data):
    return mongo.db.noticies.insert_one(data)

def editar_noticia(id, dades):
    return mongo.db.noticies.update_one({"_id": ObjectId(id)}, {"$set": dades})

def eliminar_noticia(id):
    return mongo.db.noticies.delete_one({"_id": ObjectId(id)})
