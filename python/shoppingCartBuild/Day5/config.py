import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"

    # SQLite: the whole database is a single file, created automatically the
    # first time something connects to it -- no server, no install.
    DB_FILE = os.getenv("DB_FILE", "shopping_cart.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, DB_FILE)}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123")

    PRODUCTS_API_URL = os.getenv("PRODUCTS_API_URL", "https://dummyjson.com/products")

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

    OTP_EXPIRY_MINUTES = 10
    MAX_FAILED_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_MINUTES = 15
