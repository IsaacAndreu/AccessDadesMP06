from models import Cicle
from extensions import db

def get_cicles():
    return Cicle.query.all()

def get_cicle_by_id(cicle_id):
    return Cicle.query.get(int(cicle_id))

def add_cicle(nom, descripcio):
    nou_cicle = Cicle(nom=nom, descripcio=descripcio)
    db.session.add(nou_cicle)
    db.session.commit()

def update_cicle(cicle_id, nom, descripcio):
    cicle = get_cicle_by_id(cicle_id)
    if cicle:
        cicle.nom = nom
        cicle.descripcio = descripcio
        db.session.commit()

def delete_cicle_by_id(cicle_id):
    cicle = get_cicle_by_id(cicle_id)
    if cicle:
        db.session.delete(cicle)
        db.session.commit()