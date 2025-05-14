from extensions import db

class Cicle(db.Model):
    __tablename__ = 'cicles_oracle'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    descripcio = db.Column(db.String(200))


class Grup(db.Model):
    __tablename__ = 'grups_oracle'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(50), nullable=False)


class Alumne(db.Model):
    __tablename__ = 'alumnes_oracle'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    cognoms = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    grup_id = db.Column(db.Integer, db.ForeignKey('grups_oracle.id'))
    cicle_id = db.Column(db.Integer, db.ForeignKey('cicles_oracle.id'))
    curs = db.Column(db.String(10))

    grup = db.relationship("oracle_models.GrupsOracle", backref="alumnes", foreign_keys=[grup_id])
    cicle = db.relationship("oracle_models.Cicle", backref="alumnes", foreign_keys=[cicle_id])

