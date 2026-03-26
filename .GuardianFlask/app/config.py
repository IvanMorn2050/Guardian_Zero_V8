import os
from dotenv import load_dotenv

# Cargar .env antes de leer cualquier variable
load_dotenv()

class Config:
    # --- Flask ---
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # --- Base de Datos ---
    # Lee SIEMPRE del .env — nunca hardcodear credenciales en el código
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://"
        f"{os.getenv('DB_USER', 'root')}:"
        f"{os.getenv('DB_PASSWORD', '200305')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '3306')}/"
        f"{os.getenv('DB_NAME', 'guardian_zero2')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Flask-Mail (Gmail SMTP) ---
    MAIL_SERVER         = "smtp.gmail.com"
    MAIL_PORT           = 587
    MAIL_USE_TLS        = True
    MAIL_USE_SSL        = False
    MAIL_USERNAME       = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD       = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME")

    # --- Token de recuperación (expira en 30 min) ---
    TOKEN_EXPIRATION_SECONDS = 1800