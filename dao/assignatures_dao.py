from extensions import mongo
from bson.objectid import ObjectId

# Obtenir totes les assignatures disponibles
def get_assignatures():
    return list(mongo.db.assignatures.find())

# Retornar un diccionari amb els noms de cursos indexats per ID
def get_courses_dict():
    return {
        str(course["_id"]): course["course_name"]
        for course in mongo.db.courses.find()
    }

# Obtenir la llista completa de cursos
def get_courses():
    return list(mongo.db.courses.find())

# Obtenir tots els grups. Si no n'hi ha, se n'inicialitzen uns per defecte
def get_grups():
    grups = list(mongo.db.grups.find())
    if not grups:
        mongo.db.grups.insert_many([{"nom": "A"}, {"nom": "B"}])
        grups = list(mongo.db.grups.find())
    return grups

# Obtenir tots els cicles formatius
def get_cicles():
    return list(mongo.db.cicles.find())

# Obtenir tots els professors
def get_professors():
    return list(mongo.db.professors.find())

# Afegir una nova assignatura a la base de dades
def add_assignatura(data):
    return mongo.db.assignatures.insert_one(data)

# Obtenir una assignatura concreta pel seu identificador
def get_assignatura_by_id(assignatura_id):
    try:
        return mongo.db.assignatures.find_one({"_id": ObjectId(assignatura_id)})
    except Exception:
        return None

# Actualitzar les dades d'una assignatura
def update_assignatura(assignatura_id, updated_data):
    try:
        return mongo.db.assignatures.update_one(
            {"_id": ObjectId(assignatura_id)},
            {"$set": updated_data}
        )
    except Exception:
        return None

# Eliminar una assignatura per ID
def delete_assignatura_by_id(assignatura_id):
    try:
        return mongo.db.assignatures.delete_one({"_id": ObjectId(assignatura_id)})
    except Exception:
        return None
