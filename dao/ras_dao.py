from extensions import mongo
from bson.objectid import ObjectId

def get_all_ras():
    return list(mongo.db.ras.find())

def add_ra(nom, ponderacio):
    return mongo.db.ras.insert_one({
        "nom": nom.strip(),
        "ponderacio": float(ponderacio)
    })

def get_ra_by_id(ra_id):
    return mongo.db.ras.find_one({"_id": ObjectId(ra_id)})

def update_ra(ra_id, nom, ponderacio):
    return mongo.db.ras.update_one(
        {"_id": ObjectId(ra_id)},
        {"$set": {
            "nom": nom.strip(),
            "ponderacio": float(ponderacio)
        }}
    )

def delete_ra(ra_id):
    return mongo.db.ras.delete_one({"_id": ObjectId(ra_id)})
