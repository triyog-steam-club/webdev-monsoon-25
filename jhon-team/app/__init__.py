from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flasgger import Swagger
from .config import Config

db = SQLAlchemy()
ma = Marshmallow()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    ma.init_app(app)
    
    # Swagger(app)

    with app.app_context():
        from .v1 import api_v1_bp
        app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    
    return app