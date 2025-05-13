from extensions import mongo
from bson.objectid import ObjectId

def obtenir_tots_esdeveniments():
    return list(mongo.db.esdeveniments.find())

def obtenir_esdeveniment_per_id(id):
    return mongo.db.esdeveniments.find_one({"_id": ObjectId(id)})

def afegir_esdeveniment(data):
    return mongo.db.esdeveniments.insert_one(data)

def editar_esdeveniment(id, dades):
    return mongo.db.esdeveniments.update_one({"_id": ObjectId(id)}, {"$set": dades})

def eliminar_esdeveniment(id):
    return mongo.db.esdeveniments.delete_one({"_id": ObjectId(id)})
