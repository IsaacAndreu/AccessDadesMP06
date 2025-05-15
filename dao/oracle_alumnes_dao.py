from bson import ObjectId
import re
from extensions import db
from models.oracle_models import Grup, Cicle, Alumne
from sqlalchemy.orm import joinedload

# Retorna alumnes segons els filtres opcionals de grup i cicle, carregant també les relacions
def get_alumnes_filtrats(grup_id, cicle_id):
    query = db.session.query(Alumne)

    if grup_id:
        query = query.filter(Alumne.grup_id == int(grup_id))  # Convertim el grup_id a enter per Oracle
    if cicle_id:
        query = query.filter(Alumne.cicle_id == int(cicle_id))  # Convertim el cicle_id a enter per Oracle

    return query.options(
        joinedload(Alumne.grup),
        joinedload(Alumne.cicle)
    ).all()

# Retorna tots els grups d'Oracle
def get_grups():
    return db.session.query(Grup).all()

# Retorna tots els cicles d'Oracle
def get_cicles():
    return db.session.query(Cicle).all()

# Funció per afegir un alumne
def add_alumne(nom, cognoms, email, grup_id, cicle_id, curs):
    try:
        # Helper function to validate if a string is a valid integer
        def is_valid_integer(value):
            if isinstance(value, int):
                return True
            if isinstance(value, str):
                return value.strip().isdigit()
            return False

        # Validació de 'grup_id'
        if isinstance(grup_id, ObjectId):
            grup_id_final = str(grup_id)  # Si és ObjectId, el convertim a cadena (per MongoDB)
        elif isinstance(grup_id, str) and re.match(r'^[0-9a-fA-F]{24}$', grup_id):
            grup_id_final = grup_id  # Si ja és una cadena de MongoDB
        elif is_valid_integer(grup_id):
            grup_id_final = int(grup_id)  # Si és un número per Oracle
        elif grup_id is None or grup_id == "":
            grup_id_final = None  # Permetem NULL si és opcional
        else:
            raise ValueError(f"Invalid grup_id value: {grup_id}")

        # Validació de 'cicle_id'
        if isinstance(cicle_id, ObjectId):
            cicle_id_final = str(cicle_id)
        elif isinstance(cicle_id, str) and re.match(r'^[0-9a-fA-F]{24}$', cicle_id):
            cicle_id_final = cicle_id
        elif is_valid_integer(cicle_id):
            cicle_id_final = int(cicle_id)
        elif cicle_id is None or cicle_id == "":
            cicle_id_final = None
        else:
            raise ValueError(f"Invalid cicle_id value: {cicle_id}")

        # Crear el nou alumne
        alumne = Alumne(
            nom=nom.strip(),
            cognoms=cognoms.strip(),
            email=email.strip() if email else "",
            grup_id=grup_id_final,
            cicle_id=cicle_id_final,
            curs=curs
        )

        db.session.add(alumne)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Error afegint alumne a Oracle: {e}")

def get_alumne_by_id(id):
    return db.session.query(Alumne).filter_by(id=int(id)).first()

# Actualitza les dades d’un alumne existent a Oracle
def update_alumne(id, nom, cognoms, email, grup_id, cicle_id, curs):
    alumne = get_alumne_by_id(id)
    if alumne:
        alumne.nom = nom.strip()
        alumne.cognoms = cognoms.strip()
        alumne.email = email.strip() if email else ""
        alumne.grup_id = int(grup_id) if grup_id not in (None, "") else None
        alumne.cicle_id = int(cicle_id) if cicle_id not in (None, "") else None
        alumne.curs = curs
        db.session.commit()

# Elimina un alumne a partir del seu identificador (Oracle)
def delete_alumne_by_id(id):
    alumne = get_alumne_by_id(id)
    if alumne:
        db.session.delete(alumne)
        db.session.commit()
