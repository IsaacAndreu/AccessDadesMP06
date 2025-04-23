from extensions import mongo
from bson.objectid import ObjectId

def get_all_grups():
    return list(mongo.db.grups.find())

def add_grup(nom):
    return mongo.db.grups.insert_one({"nom": nom.strip()})

def get_grup_by_id(grup_id):
    return mongo.db.grups.find_one({"_id": ObjectId(grup_id)})

def update_grup(grup_id, nom):
    return mongo.db.grups.update_one(
        {"_id": ObjectId(grup_id)},
        {"$set": {"nom": nom.strip()}}
    )

def delete_grup(grup_id):
    return mongo.db.grups.delete_one({"_id": ObjectId(grup_id)})
