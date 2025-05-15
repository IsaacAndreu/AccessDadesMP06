from flask import Flask
from config import Config
from extensions import mongo, db
from routes.cicles import cicles_bp
from routes.grups import grups_bp
from werkzeug.security import generate_password_hash
from routes.esdeveniments import esdeveniments_bp
from utils.create_oracle_procedures import crear_procediments_oracle  # Importem la funció

def crear_admin_per_defecte():
    """
    Funció per crear un usuari administrador per defecte si no existeix ja a la base de dades.
    Es pot modificar la contrasenya per millorar la seguretat.
    """
    admin_email = "admin@escolaexemplar.com"
    admin = mongo.db.professors.find_one({"email": admin_email})

    if not admin:
        # Si no existeix un usuari admin, es crea
        mongo.db.professors.insert_one({
            "nom": "Admin",
            "cognoms": "Principal",
            "email": admin_email,
            "password": generate_password_hash("admin123"),  # Pots canviar la contrasenya
            "rol": "admin",  # Rol de l'usuari com a administrador
            "telefon": "",
            "idioma": "ca",  # Idioma per defecte
            "tema": "clar",  # Tema visual per defecte
            "documents": [],  # Documents associats a l'usuari
            "foto_perfil": ""  # Foto de perfil per defecte (pot ser actualitzada)
        })
        print("✅ Usuari administrador creat per defecte.")
    else:
        print("ℹ️ Ja existeix un usuari admin.")

def create_app():
    """
    Funció per crear la instància de l'aplicació Flask, configurar-la i registrar els blueprints.
    """
    app = Flask(__name__)
    app.config.from_object(Config)  # Carrega la configuració des de la classe Config

    mongo.init_app(app)  # Inicialitza la connexió a MongoDB
    db.init_app(app)  # Inicialitza la connexió a SQLAlchemy

    # Crear les taules i procediments si calen
    with app.app_context():
        db.create_all()  # Crear les taules a la base de dades si no existeixen

        # Crear procediments Oracle
        crear_procediments_oracle()  # Crea els procediments necessaris per Oracle

        # Crear l'usuari administrador si no existeix
        crear_admin_per_defecte()

    # Registre dels blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.alumnes import alumnes_bp
    from routes.assignatures import assignatures_bp
    from routes.professors import professors_bp
    from routes.notes import notes_bp
    from routes.noticies import noticies_bp  # Nou import

    # Registrar tots els blueprints
    app.register_blueprint(main_bp)  # Pàgina principal
    app.register_blueprint(auth_bp)  # Autenticació
    app.register_blueprint(alumnes_bp, url_prefix="/alumnes")  # Alumnes amb el prefix '/alumnes'
    app.register_blueprint(assignatures_bp, url_prefix="/assignatures")  # Assignatures amb el prefix '/assignatures'
    app.register_blueprint(grups_bp, url_prefix="/grups")  # Grups amb el prefix '/grups'
    app.register_blueprint(professors_bp, url_prefix="/professors")  # Professors amb el prefix '/professors'
    app.register_blueprint(cicles_bp, url_prefix="/cicles")  # Cicles amb el prefix '/cicles'
    app.register_blueprint(notes_bp, url_prefix="/notes")  # Notes amb el prefix '/notes'
    app.register_blueprint(noticies_bp, url_prefix="/noticies")  # Notícies amb el prefix '/noticies' (nou)
    app.register_blueprint(esdeveniments_bp, url_prefix="/esdeveniments")  # Esdeveniments amb el prefix '/esdeveniments'

    return app

# Inicia l'aplicació
if __name__ == "__main__":
    app = create_app()  # Crear i configurar l'aplicació
    app.run(debug=True, host="0.0.0.0")  # Llençar l'aplicació en mode debug i accessible externament
