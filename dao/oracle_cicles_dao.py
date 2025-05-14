from models import Cicle
from extensions import db

# Retorna tots els cicles formatius disponibles
def get_cicles():
    return Cicle.query.all()

# Retorna un cicle pel seu identificador
def get_cicle_by_id(cicle_id):
    return Cicle.query.get(int(cicle_id))

# Afegeix un nou cicle a la base de dades
def add_cicle(nom, descripcio):
    nou_cicle = Cicle(
        nom=nom.strip(),
        descripcio=descripcio.strip() if descripcio else ""
    )
    db.session.add(nou_cicle)
    db.session.commit()

# Actualitza un cicle existent amb les dades subministrades
def update_cicle(cicle_id, nom, descripcio):
    cicle = get_cicle_by_id(cicle_id)
    if cicle:
        cicle.nom = nom.strip()
        cicle.descripcio = descripcio.strip() if descripcio else ""
        db.session.commit()

# Elimina un cicle per identificador
def delete_cicle_by_id(cicle_id):
    cicle = get_cicle_by_id(cicle_id)
    if cicle:
        db.session.delete(cicle)
        db.session.commit()
