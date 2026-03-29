import os
import base64
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_mail import Mail

from app.config import Config
from app.models import db, Usuario

mail = Mail()
login_manager = LoginManager()

# Ruta absoluta a la carpeta app/ — resuelve el problema de templates en blanco
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(_BASE_DIR, "templates"),
        static_folder=os.path.join(_BASE_DIR, "static"),
    )
    app.config.from_object(Config)

    # ── Filtros Jinja2 ──
    @app.template_filter("b64encode")
    def b64encode_filter(data):
        if data is None:
            return ""
        return base64.b64encode(data).decode("utf-8")

    # ── Extensiones ──
    db.init_app(app)
    mail.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view            = "auth.login"
    login_manager.login_message         = "Inicia sesión para acceder a esta página."
    login_manager.login_message_category = "warning"

    # ── User loader ──
    @login_manager.user_loader
    def load_user(user_id: str):
        return Usuario.query.get(int(user_id))

    # ── Blueprints ──
    from app.routers import auth_bp, dashboard_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    # Ruta raíz → login
    @app.route("/")
    def root():
        return redirect(url_for("auth.login"))

    return app