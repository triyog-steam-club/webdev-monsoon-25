from flask import Flask
from flasgger import Swagger
from .config import Config

swagger_config = {
    'title': 'VISION Team API', 
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

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    Swagger(app, config=swagger_config)

    from .v1 import bp as v1_blueprint
    app.register_blueprint(v1_blueprint, url_prefix='/api/v1')

    return app