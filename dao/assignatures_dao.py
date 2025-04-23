from extensions import mongo
from bson.objectid import ObjectId

def get_assignatures():
    return list(mongo.db.assignatures.find())

def get_courses_dict():
    return {str(course["_id"]): course["course_name"] for course in mongo.db.courses.find()}

def get_courses():
    return list(mongo.db.courses.find())

def get_grups():
    grups = list(mongo.db.grups.find())
    if not grups:
        mongo.db.grups.insert_many([{"nom": "A"}, {"nom": "B"}])
        grups = list(mongo.db.grups.find())
    return grups

def get_cicles():
    return list(mongo.db.cicles.find())

def get_professors():
    return list(mongo.db.professors.find())

def add_assignatura(data):
    return mongo.db.assignatures.insert_one(data)

def get_assignatura_by_id(assignatura_id):
    return mongo.db.assignatures.find_one({"_id": ObjectId(assignatura_id)})

def update_assignatura(assignatura_id, updated_data):
    return mongo.db.assignatures.update_one(
        {"_id": ObjectId(assignatura_id)},
        {"$set": updated_data}
    )

def delete_assignatura_by_id(assignatura_id):
    return mongo.db.assignatures.delete_one({"_id": ObjectId(assignatura_id)})
