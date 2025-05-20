# dao/oracle_academics_dao.py

import cx_Oracle
from extensions import oracle_connection

def get_cicles_oracle():
    """
    Retorna tots els cicles formatius de l'Oracle
    com a llista de diccionaris amb claus '_id' i 'nom'.
    """
    query = "SELECT id, nom FROM cicles ORDER BY nom"
    with oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    # Convertim cada fila en diccionari
    return [{"_id": row[0], "nom": row[1]} for row in rows]

def get_grups_oracle():
    """
    Retorna tots els grups de l'Oracle
    com a llista de diccionaris amb claus '_id' i 'nom'.
    """
    query = "SELECT id, nom FROM grups ORDER BY nom"
    with oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    return [{"_id": row[0], "nom": row[1]} for row in rows]

# dao/oracle_academics_dao.py
from extensions import db
from models import Grup, Cicle

def get_grups_oracle():
    # Ara retorna instàncies ORM, no dicts
    return Grup.query.order_by(Grup.nom).all()

def get_cicles_oracle():
    return Cicle.query.order_by(Cicle.nom).all()
