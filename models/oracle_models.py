from extensions import db

class Grup(db.Model):
    __tablename__ = 'grups_oracle'
    __table_args__ = {'extend_existing': True}  # Afegir per evitar definicions duplicades

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)


class Cicle(db.Model):
    __tablename__ = 'cicles_oracle'
    __table_args__ = {'extend_existing': True}  # Afegir per evitar definicions duplicades

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    descripcio = db.Column(db.String(200))  # Afegeix el camp descripcio


class Alumne(db.Model):
    __tablename__ = 'alumnes_oracle'
    __table_args__ = {'extend_existing': True}  # Afegir per evitar definicions duplicades

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    cognoms = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    grup_id = db.Column(db.Integer, db.ForeignKey('grups_oracle.id'))  # Clau forana per Grup
    cicle_id = db.Column(db.Integer, db.ForeignKey('cicles_oracle.id'))  # Clau forana per Cicle
    curs = db.Column(db.String(10))

    # Relacions amb Grup i Cicle
    grup = db.relationship('Grup', backref='alumnes', foreign_keys=[grup_id])
    cicle = db.relationship('Cicle', backref='alumnes', foreign_keys=[cicle_id])
