from extensions import mongo
from bson.objectid import ObjectId

# Obtenir alumnes amb filtres opcionals (grup_id i/o cicle_id)
def get_alumnes_filtrats(grup_id=None, cicle_id=None):
    filtre = {}
    if grup_id:
        filtre["grup"] = grup_id  # Assegura't que és string si el guardes així a Mongo
    if cicle_id:
        try:
            filtre["cicle_id"] = ObjectId(cicle_id)
        except Exception:
            pass  # No afegeix el filtre si no és un ObjectId vàlid
    return list(mongo.db.alumnes.find(filtre))

# Obtenir tots els grups (i inicialitzar si està buit)
def get_grups():
    grups = list(mongo.db.grups.find())
    if not grups:
        mongo.db.grups.insert_many([{"nom": "A"}, {"nom": "B"}])
        grups = list(mongo.db.grups.find())
    return grups

# Obtenir tots els cicles
def get_cicles():
    return list(mongo.db.cicles.find())

# Afegir un nou alumne
def add_alumne(nom, cognoms, email, grup, cicle_id, curs):
    try:
        return mongo.db.alumnes.insert_one({
            "nom": nom.strip(),
            "cognoms": cognoms.strip(),
            "email": email.strip() if email else "",
            "grup": grup,
            "cicle_id": ObjectId(cicle_id),
            "curs": curs
        })
    except Exception as e:
        raise ValueError(f"Error afegint alumne: {e}")

# Buscar alumne per ID
def get_alumne_by_id(alumne_id):
    try:
        return mongo.db.alumnes.find_one({"_id": ObjectId(alumne_id)})
    except Exception:
        return None

# Actualitzar dades d’un alumne existent
def update_alumne(alumne_id, nom, cognoms, email, grup, cicle_id, curs):
    try:
        return mongo.db.alumnes.update_one(
            {"_id": ObjectId(alumne_id)},
            {"$set": {
                "nom": nom.strip(),
                "cognoms": cognoms.strip(),
                "email": email.strip() if email else "",
                "grup": grup,
                "cicle_id": ObjectId(cicle_id),
                "curs": curs
            }}
        )
    except Exception as e:
        raise ValueError(f"Error actualitzant alumne: {e}")

# Eliminar un alumne per ID
def delete_alumne_by_id(alumne_id):
    try:
        return mongo.db.alumnes.delete_one({"_id": ObjectId(alumne_id)})
    except Exception as e:
        raise ValueError(f"Error eliminant alumne: {e}")
