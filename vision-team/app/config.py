import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    EDAMAM_APP_ID = os.environ.get('EDAMAM_APP_ID')
    EDAMAM_APP_KEY = os.environ.get('EDAMAM_APP_KEY')
    EDAMAM_API_ENDPOINT = "https://api.edamam.com/api/recipes/v2"

    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')