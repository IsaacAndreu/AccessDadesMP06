from flask import Flask
from config import Config
from extensions import mongo, db
from routes.cicles import cicles_bp
from routes.grups import grups_bp
from models.oracle_models import GrupsOracle, Cicle
from models import oracle_models
from werkzeug.security import generate_password_hash
from bson.objectid import ObjectId
from routes.esdeveniments import esdeveniments_bp

def crear_admin_per_defecte():
    admin_email = "admin@escolaexemplar.com"
    admin = mongo.db.professors.find_one({"email": admin_email})
    if not admin:
        mongo.db.professors.insert_one({
            "nom": "Admin",
            "cognoms": "Principal",
            "email": admin_email,
            "password": generate_password_hash("admin123"),  # 🔐 pots canviar-la
            "rol": "admin",
            "telefon": "",
            "idioma": "ca",
            "tema": "clar",
            "documents": [],
            "foto_perfil": ""
        })
        print("✅ Usuari administrador creat per defecte.")
    else:
        print("ℹ️ Ja existeix un usuari admin.")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mongo.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

        # Crear procediments Oracle
        from utils.create_oracle_procedures import crear_procediments_oracle
        crear_procediments_oracle()

        # ✅ Crear l'usuari admin
        crear_admin_per_defecte()

    # Blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.alumnes import alumnes_bp
    from routes.assignatures import assignatures_bp
    from routes.professors import professors_bp
    from routes.notes import notes_bp
    from routes.noticies import noticies_bp  # 🔥 Nou import

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(alumnes_bp, url_prefix="/alumnes")
    app.register_blueprint(assignatures_bp, url_prefix="/assignatures")
    app.register_blueprint(grups_bp, url_prefix="/grups")
    app.register_blueprint(professors_bp, url_prefix="/professors")
    app.register_blueprint(cicles_bp, url_prefix="/cicles")
    app.register_blueprint(notes_bp, url_prefix="/notes")
    app.register_blueprint(noticies_bp, url_prefix="/noticies")  # 🔥 Nou registre
    app.register_blueprint(esdeveniments_bp, url_prefix="/esdeveniments")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0")

