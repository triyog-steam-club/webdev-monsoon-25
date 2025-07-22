from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flasgger import Swagger
from .config import Config

db = SQLAlchemy()
ma = Marshmallow()

swagger_config = {
    'title': 'Jhon Team API', 
    'uiversion': 3,
    'openapi': '3.0.2',
    'specs': [
        {
            'endpoint': 'apispec_1',
            'route': '/swagger.json',
            'rule_filter': lambda rule: True,  
            'model_filter': lambda tag: True,  
        }
    ],
    'headers': [],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route': '/docs/'
}

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    ma.init_app(app)
    Swagger(app, config=swagger_config)

    with app.app_context():
        from .v1 import api_v1_bp
        
        db.create_all()
        app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    
    return app