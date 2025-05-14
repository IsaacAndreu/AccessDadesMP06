from extensions import db
from sqlalchemy.orm import joinedload
from models import Alumne, Grup, Cicle

# Retorna alumnes segons els filtres opcionals de grup i cicle, carregant també les relacions
def get_alumnes_filtrats(grup_id, cicle_id):
    query = db.session.query(Alumne)

    if grup_id:
        query = query.filter(Alumne.grup_id == int(grup_id))
    if cicle_id:
        query = query.filter(Alumne.cicle_id == int(cicle_id))

    return query.options(
        joinedload(Alumne.grup),
        joinedload(Alumne.cicle)
    ).all()

# Retorna tots els grups disponibles
def get_grups():
    return db.session.query(Grup).all()

# Retorna tots els cicles formatius
def get_cicles():
    return db.session.query(Cicle).all()

# Insereix un nou alumne a la base de dades
def add_alumne(nom, cognoms, email, grup, cicle_id, curs):
    nou_alumne = Alumne(
        nom=nom,
        cognoms=cognoms,
        email=email,
        grup_id=int(grup),
        cicle_id=int(cicle_id),
        curs=curs
    )
    db.session.add(nou_alumne)
    db.session.commit()

# Cerca un alumne pel seu identificador
def get_alumne_by_id(id):
    return db.session.query(Alumne).filter_by(id=int(id)).first()

# Actualitza les dades d’un alumne existent
def update_alumne(id, nom, cognoms, email, grup, cicle_id, curs):
    alumne = get_alumne_by_id(id)
    if alumne:
        alumne.nom = nom
        alumne.cognoms = cognoms
        alumne.email = email
        alumne.grup_id = int(grup)
        alumne.cicle_id = int(cicle_id)
        alumne.curs = curs
        db.session.commit()

# Elimina un alumne a partir del seu identificador
def delete_alumne_by_id(id):
    alumne = get_alumne_by_id(id)
    if alumne:
        db.session.delete(alumne)
        db.session.commit()
