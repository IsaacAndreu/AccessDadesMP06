import os

MONGO = "mongo"
ORACLE = "oracle"
ZODB = "zodb"

# Determinar la base de dades activa per a determinats mòduls
ACTIVE_DB = os.getenv("ACTIVE_DB", MONGO)  # Aquesta variable es pot configurar a .env

# Funció per gestionar la base de dades activa per a cada tipus de dada
def get_db_connection(entity_type):
    """
    A partir del tipus d'entitat (alumnes, grups, notícies...), seleccionem la base de dades correcta.
    :param entity_type: Tipus d'entitat (ex. 'alumne', 'grup', 'noticies', etc.)
    :return: La base de dades activa per a aquest tipus d'entitat.
    """
    if entity_type == "alumne" or entity_type == "grups" or entity_type == "cicles":
        # Usarem Oracle per alumnes, grups i cicles
        return ORACLE
    else:
        # Altres entitats, per exemple, notícies, assignatures, etc., usen MongoDB
        return MONGO

# Aquesta funció pot ser útil per gestionar la connexió directa a la base de dades
def get_database_connection():
    """
    Retorna la base de dades activa depenent de la configuració.
    Utilitza la variable d'entorn per determinar si utilitzar Oracle o MongoDB.
    """
    if ACTIVE_DB == ORACLE:
        return "oracle_connection_object"  # Connexió Oracle
    elif ACTIVE_DB == MONGO:
        return "mongo_connection_object"  # Connexió MongoDB
    else:
        raise ValueError(f"Base de dades {ACTIVE_DB} no suportada.")
