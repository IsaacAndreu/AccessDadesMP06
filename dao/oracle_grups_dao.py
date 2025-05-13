from extensions import db
from models import Grup

def get_grups():
    return Grup.query.all()

def get_grup_by_id(grup_id):
    return Grup.query.get(int(grup_id))

def add_grup(nom):
    nou_grup = Grup(nom=nom)
    db.session.add(nou_grup)
    db.session.commit()

def update_grup(grup_id, nom):
    grup = get_grup_by_id(grup_id)
    if grup:
        grup.nom = nom
        db.session.commit()

def delete_grup_by_id(grup_id):
    grup = get_grup_by_id(grup_id)
    if grup:
        db.session.delete(grup)
        db.session.commit()
