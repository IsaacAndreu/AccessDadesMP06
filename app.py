from flask import Flask
from config import Config
from extensions import mongo  # Importem mongo des de extensions
from routes.cicles import cicles_bp
from routes.grups import grups_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicialitzem mongo amb l'app
    mongo.init_app(app)

    # Importem i registrem els blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.alumnes import alumnes_bp
    from routes.assignatures import assignatures_bp
    from routes.professors import professors_bp
    from routes.notes import notes_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(alumnes_bp, url_prefix="/alumnes")
    app.register_blueprint(assignatures_bp, url_prefix="/assignatures")
    app.register_blueprint(grups_bp, url_prefix="/grups")
    app.register_blueprint(professors_bp, url_prefix="/professors")
    app.register_blueprint(cicles_bp, url_prefix="/cicles")

    app.register_blueprint(notes_bp, url_prefix="/notes")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
