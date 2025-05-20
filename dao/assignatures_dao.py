from extensions import mongo
from bson.objectid import ObjectId
from dao.oracle_academics_dao import get_cicles_oracle, get_grups_oracle
from dao.oracle_academics_dao import get_grups_oracle as get_grups, \
                                     get_cicles_oracle as get_cicles

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

# Obtenir tots els grups formatius des de l’Oracle
def get_grups():
    return get_grups_oracle()

# Obtenir tots els cicles formatius des de l’Oracle
def get_cicles():
    return get_cicles_oracle()

# Obtenir tots els professors
# (segueix agafant-los de Mongo, o ajusta si vols passar-los també d'Oracle)
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

# Obtenir assignatures amb els seus RAs (per select)
def get_assignatures_amb_ras():
    assignatures = list(get_assignatures())
    for a in assignatures:
        if "ras" not in a:
            a["ras"] = []  # Assegurem la clau per evitar errors al frontend
    return assignatures