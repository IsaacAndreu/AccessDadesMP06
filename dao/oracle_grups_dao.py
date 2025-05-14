from extensions import db
from models import Grup

# Retorna tots els grups disponibles
def get_grups():
    return Grup.query.all()

# Retorna un grup pel seu identificador
def get_grup_by_id(grup_id):
    return Grup.query.get(int(grup_id))

# Afegeix un nou grup a la base de dades
def add_grup(nom):
    nou_grup = Grup(nom=nom.strip())
    db.session.add(nou_grup)
    db.session.commit()

# Actualitza el nom d’un grup existent
def update_grup(grup_id, nom):
    grup = get_grup_by_id(grup_id)
    if grup:
        grup.nom = nom.strip()
        db.session.commit()

# Elimina un grup per identificador
def delete_grup_by_id(grup_id):
    grup = get_grup_by_id(grup_id)
    if grup:
        db.session.delete(grup)
        db.session.commit()
