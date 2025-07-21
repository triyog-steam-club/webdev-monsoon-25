import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

from .config import config_by_name

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config_by_name[config_name])
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    CORS(app, resources={r"/v1/*": {"origins": "*"}})

    Swagger(app, config=app.config['SWAGGER'])

    from .v1 import v1_blueprint
    app.register_blueprint(v1_blueprint)

    @app.route('/health')
    def health():
        return "OK"
    
    with app.app_context():
        db.create_all()

    return app