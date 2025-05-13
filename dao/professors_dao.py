from extensions import mongo
from bson.objectid import ObjectId

# --- Professors ---
def get_all_professors():
    return list(mongo.db.professors.find())

def get_professor_by_id(prof_id):
    return mongo.db.professors.find_one({"_id": ObjectId(prof_id)})

def add_professor(nom, cognoms, email, rol="professor"):
    return mongo.db.professors.insert_one({
        "nom": nom.strip(),
        "cognoms": cognoms.strip(),
        "email": email.strip(),
        "rol": rol
    })


def update_professor(prof_id, nom, cognoms, email):
    return mongo.db.professors.update_one(
        {"_id": ObjectId(prof_id)},
        {"$set": {
            "nom": nom.strip(),
            "cognoms": cognoms.strip(),
            "email": email.strip()
        }}
    )

def delete_professor(prof_id):
    return mongo.db.professors.delete_one({"_id": ObjectId(prof_id)})

# --- Cursos ---
def get_all_courses():
    return list(mongo.db.courses.find())

def get_course_by_id(course_id):
    return mongo.db.courses.find_one({"_id": ObjectId(course_id)})

def add_course(course_name, description, teacher_id):
    return mongo.db.courses.insert_one({
        "course_name": course_name,
        "description": description,
        "teacher_id": teacher_id
    })

def update_course(course_id, course_name, description):
    return mongo.db.courses.update_one(
        {"_id": ObjectId(course_id)},
        {"$set": {"course_name": course_name, "description": description}}
    )

def delete_course(course_id):
    return mongo.db.courses.delete_one({"_id": ObjectId(course_id)})

# --- Altres ---
def get_assignatures_by_teacher(teacher_id):
    return list(mongo.db.assignatures.find({"professor_ids": ObjectId(teacher_id)}))

def get_cicles_dict():
    return {str(c["_id"]): c["nom"] for c in mongo.db.cicles.find()}

def get_grups_dict():
    return {str(g["_id"]): g["nom"] for g in mongo.db.grups.find()}

def update_professor_perfil(prof_id, dades, nova_password=None, foto_filename=None):

    update_fields = {
        "nom": dades.get("nom", "").strip(),
        "cognoms": dades.get("cognoms", "").strip(),
        "telefon": dades.get("telefon", "").strip(),
        "idioma": dades.get("idioma", "ca"),
        "tema": dades.get("tema", "clar")
    }

    if nova_password:
        update_fields["password"] = nova_password

    if foto_filename:
        update_fields["foto_perfil"] = foto_filename

    return mongo.db.professors.update_one(
        {"_id": ObjectId(prof_id)},
        {"$set": update_fields}
    )
