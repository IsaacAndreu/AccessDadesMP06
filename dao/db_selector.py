import os

MONGO = "mongo"
ORACLE = "oracle"
ZODB = "zodb"

# Determinar la base de dades activa per a determinats mòduls
ACTIVE_DB = os.getenv("ACTIVE_DB", MONGO)  # Aquesta variable es pot configurar a .env

# Funció per gestionar la base de dades activa per a cada tipus de dada
def get_db_connection(entity_type):
    if entity_type == "alumne" or entity_type == "grups" or entity_type == "cicles":
        # Usarem Oracle per alumnes, grups i cicles
        return ORACLE
    else:
        # Altres entitats, per exemple, notícies, assignatures, etc., usen MongoDB
        return MONGO

# Aquesta funció pot ser útil per gestionar la connexió directa a la base de dades
def get_database_connection():

    if ACTIVE_DB == ORACLE:
        return "oracle_connection_object"  # Connexió Oracle
    elif ACTIVE_DB == MONGO:
        return "mongo_connection_object"  # Connexió MongoDB
    else:
        raise ValueError(f"Base de dades {ACTIVE_DB} no suportada.")
