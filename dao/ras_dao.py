from extensions import mongo
from bson.objectid import ObjectId

def get_all_ras():
    """
    Retorna tots els resultats d'aprenentatge (RA) disponibles.
    """
    return list(mongo.db.ras.find())

def add_ra(nom, ponderacio):
    """
    Afegeix un nou resultat d'aprenentatge.

    Args:
        nom (str): Nom del RA.
        ponderacio (float o str): Percentatge de ponderació del RA.
    """
    return mongo.db.ras.insert_one({
        "nom": nom.strip(),
        "ponderacio": float(ponderacio)
    })

def get_ra_by_id(ra_id):
    """
    Obté un RA pel seu identificador únic.

    Args:
        ra_id (str): ID del RA en format cadena.

    Returns:
        dict o None: El RA si existeix, None en cas contrari.
    """
    return mongo.db.ras.find_one({"_id": ObjectId(ra_id)})

def update_ra(ra_id, nom, ponderacio):
    """
    Actualitza un resultat d'aprenentatge existent.

    Args:
        ra_id (str): ID del RA.
        nom (str): Nou nom del RA.
        ponderacio (float o str): Nova ponderació.
    """
    return mongo.db.ras.update_one(
        {"_id": ObjectId(ra_id)},
        {"$set": {
            "nom": nom.strip(),
            "ponderacio": float(ponderacio)
        }}
    )

def delete_ra(ra_id):
    """
    Elimina un resultat d'aprenentatge pel seu ID.

    Args:
        ra_id (str): ID del RA a eliminar.

    Returns:
        DeleteResult: Resultat de l'operació de supressió.
    """
    return mongo.db.ras.delete_one({"_id": ObjectId(ra_id)})
