import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', f"sqlite:///{os.path.join(basedir, 'app.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GEMINI_API_KEYS = os.environ.get('GEMINI_API_KEYS', '').split(',')