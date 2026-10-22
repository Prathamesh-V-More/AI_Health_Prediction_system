id="k4gk8l"
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)


class Config:

    # ---------------------------------------------------------
    # BASIC CONFIG
    # ---------------------------------------------------------
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "health-ai-secret-2024"
    )

    SQLALCHEMY_DATABASE_URI = "sqlite:///health_ai.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # ---------------------------------------------------------
    # MAIL CONFIGURATION
    # ---------------------------------------------------------
    MAIL_SERVER = "smtp.gmail.com"

    MAIL_PORT = 587

    MAIL_USE_TLS = True

    MAIL_USE_SSL = False

    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")

    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")

    MAIL_SUPPRESS_SEND = False


    # ---------------------------------------------------------
    # FILE UPLOAD
    # ---------------------------------------------------------
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(__file__),
        "static",
        "uploads"
    )

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    ALLOWED_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg"
    }


    # ---------------------------------------------------------
    # SESSION
    # ---------------------------------------------------------
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    OTP_EXPIRY_MINUTES = 10

