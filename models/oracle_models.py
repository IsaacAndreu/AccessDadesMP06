from extensions import db

class GrupsOracle(db.Model):
    __tablename__ = 'grups_oracle'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)

class CiclesOracle(db.Model):
    __tablename__ = 'cicles_oracle'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
