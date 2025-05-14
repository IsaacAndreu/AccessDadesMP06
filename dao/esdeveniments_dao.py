from extensions import mongo
from bson.objectid import ObjectId

# Retorna una llista amb tots els esdeveniments de la base de dades
def obtenir_tots_esdeveniments():
    return list(mongo.db.esdeveniments.find())

# Retorna un esdeveniment concret pel seu identificador únic
def obtenir_esdeveniment_per_id(id):
    try:
        return mongo.db.esdeveniments.find_one({"_id": ObjectId(id)})
    except Exception:
        return None

# Insereix un nou esdeveniment a la base de dades
def afegir_esdeveniment(data):
    return mongo.db.esdeveniments.insert_one(data)

# Actualitza un esdeveniment amb les noves dades proporcionades
def editar_esdeveniment(id, dades):
    try:
        return mongo.db.esdeveniments.update_one(
            {"_id": ObjectId(id)},
            {"$set": dades}
        )
    except Exception:
        return None

# Elimina un esdeveniment a partir del seu ID
def eliminar_esdeveniment(id):
    try:
        return mongo.db.esdeveniments.delete_one({"_id": ObjectId(id)})
    except Exception:
        return None
