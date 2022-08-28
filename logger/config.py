"""Flask configuration."""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '..', '.env'))


class Config:
    """Set Flask config variables."""

    FLASK_ENV = 'development'
    FLASK_APP = 'logger.application'
    TESTING = True
    SECRET_KEY = environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for Flask application")
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
    MAX_CONTENT_LENGTH = 1024 * 1024 * 2