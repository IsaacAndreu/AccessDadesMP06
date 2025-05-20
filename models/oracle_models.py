from extensions import db

# Taula d’associació Assignatura ↔ Grup
assignatura_grup = db.Table(
    'assignatura_grup_oracle',
    db.Column('assignatura_id', db.Integer,
              db.ForeignKey('assignatures_oracle.id'),
              primary_key=True),
    db.Column('grup_id', db.Integer,
              db.ForeignKey('grups_oracle.id'),
              primary_key=True),
    extend_existing=True
)

class Assignatura(db.Model):
    __tablename__ = 'assignatures_oracle'
    __table_args__ = {'extend_existing': True}

    id       = db.Column(db.Integer, primary_key=True)
    nom      = db.Column(db.String(100), nullable=False)
    cicle_id = db.Column(db.Integer,
                         db.ForeignKey('cicles_oracle.id'),
                         nullable=False)

    # Relacions
    cicle    = db.relationship('Cicle',
                               backref=db.backref('assignatures', lazy='select'),
                               foreign_keys=[cicle_id])
    grups    = db.relationship('Grup',
                               secondary=assignatura_grup,
                               backref=db.backref('assignatures', lazy='select'),
                               lazy='select')  # pots posar 'joined' per eager

# Models que ja tens
class Grup(db.Model):
    __tablename__ = 'grups_oracle'
    __table_args__ = {'extend_existing': True}

    id   = db.Column(db.Integer, primary_key=True)
    nom  = db.Column(db.String(50), nullable=False)

class Cicle(db.Model):
    __tablename__ = 'cicles_oracle'
    __table_args__ = {'extend_existing': True}

    id          = db.Column(db.Integer, primary_key=True)
    nom         = db.Column(db.String(100), nullable=False)
    descripcio  = db.Column(db.String(200))

class Alumne(db.Model):
    __tablename__ = 'alumnes_oracle'
    __table_args__ = {'extend_existing': True}

    id        = db.Column(db.Integer, primary_key=True)
    nom       = db.Column(db.String(50), nullable=False)
    cognoms   = db.Column(db.String(100), nullable=False)
    email     = db.Column(db.String(100))
    grup_id   = db.Column(db.Integer,
                          db.ForeignKey('grups_oracle.id'))
    cicle_id  = db.Column(db.Integer,
                          db.ForeignKey('cicles_oracle.id'))
    curs      = db.Column(db.String(10))

    grup      = db.relationship('Grup',
                                backref='alumnes',
                                foreign_keys=[grup_id])
    cicle     = db.relationship('Cicle',
                                backref='alumnes',
                                foreign_keys=[cicle_id])
