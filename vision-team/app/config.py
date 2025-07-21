import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    X_API_KEY = os.environ.get('X_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')


    SWAGGER = {
        'title': 'Vision Team API',
        'uiversion': 3,
        'openapi': '3.0.2',
        'specs': [
            {
                'endpoint': 'apispec_1',
                'route': '/swagger.json',
                'rule_filter': lambda rule: True,  # all in
                'model_filter': lambda tag: True,  # all in
            }
        ],
        'headers': [],
        'static_url_path': '/flasgger_static',
        'swagger_ui': True,
        'specs_route': '/docs/'  
    }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}