from extensions import mongo
from bson.objectid import ObjectId

# --- Professors ---

def get_all_professors():
    """Retorna tots els professors registrats."""
    return list(mongo.db.professors.find())

def get_professor_by_id(prof_id):
    """Retorna un professor pel seu ID."""
    return mongo.db.professors.find_one({"_id": ObjectId(prof_id)})

def add_professor(nom, cognoms, email, rol="professor"):
    """Afegeix un nou professor a la base de dades."""
    return mongo.db.professors.insert_one({
        "nom": nom.strip(),
        "cognoms": cognoms.strip(),
        "email": email.strip(),
        "rol": rol
    })

def update_professor(prof_id, nom, cognoms, email):
    """Actualitza les dades bàsiques d’un professor existent."""
    return mongo.db.professors.update_one(
        {"_id": ObjectId(prof_id)},
        {"$set": {
            "nom": nom.strip(),
            "cognoms": cognoms.strip(),
            "email": email.strip()
        }}
    )

def delete_professor(prof_id):
    """Elimina un professor pel seu ID."""
    return mongo.db.professors.delete_one({"_id": ObjectId(prof_id)})

# --- Cursos ---

def get_all_courses():
    """Retorna tots els cursos disponibles."""
    return list(mongo.db.courses.find())

def get_course_by_id(course_id):
    """Retorna un curs pel seu ID."""
    return mongo.db.courses.find_one({"_id": ObjectId(course_id)})

def add_course(course_name, description, teacher_id):
    """Afegeix un nou curs associat a un professor."""
    return mongo.db.courses.insert_one({
        "course_name": course_name.strip(),
        "description": description.strip(),
        "teacher_id": teacher_id
    })

def update_course(course_id, course_name, description):
    """Actualitza el nom i la descripció d’un curs existent."""
    return mongo.db.courses.update_one(
        {"_id": ObjectId(course_id)},
        {"$set": {
            "course_name": course_name.strip(),
            "description": description.strip()
        }}
    )

def delete_course(course_id):
    """Elimina un curs pel seu ID."""
    return mongo.db.courses.delete_one({"_id": ObjectId(course_id)})

# --- Altres ---

def get_assignatures_by_teacher(teacher_id):
    """Retorna totes les assignatures assignades a un professor donat."""
    return list(mongo.db.assignatures.find({"professor_ids": ObjectId(teacher_id)}))

def get_cicles_dict():
    """Retorna un diccionari de cicles amb ID com a clau i nom com a valor."""
    return {str(c["_id"]): c["nom"] for c in mongo.db.cicles.find()}

def get_grups_dict():
    """Retorna un diccionari de grups amb ID com a clau i nom com a valor."""
    return {str(g["_id"]): g["nom"] for g in mongo.db.grups.find()}

def update_professor_perfil(prof_id, dades, nova_password=None, foto_filename=None):
    """Actualitza el perfil d’un professor amb les dades proporcionades."""
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
