from extensions import mongo
from bson.objectid import ObjectId
from sqlalchemy.orm import joinedload

# Retorna totes les notícies ordenades per data de forma descendent (més recents primer)
def get_all_noticies():
    return list(mongo.db.noticies.find().sort("data", -1))

# Retorna una notícia concreta pel seu identificador
def get_noticia_by_id(id):
    return mongo.db.noticies.find_one({"_id": ObjectId(id)})

# Insereix una nova notícia a la col·lecció
def afegir_noticia(data):
    return mongo.db.noticies.insert_one(data)

# Actualitza una notícia existent amb noves dades
def editar_noticia(id, dades):
    return mongo.db.noticies.update_one(
        {"_id": ObjectId(id)},
        {"$set": dades}
    )

# Elimina una notícia pel seu identificador
def eliminar_noticia(id):
    return mongo.db.noticies.delete_one({"_id": ObjectId(id)})
