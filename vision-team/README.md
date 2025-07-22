> Author: [Sitanshu Shrestha](https://github.com/itssitanshu)  
> Developed for STEAM Club's Web-Development Competition. Team: Vision Sapkota, Aaditya Poudel, Kritistha Khatiwada

# NutriAI: Personalized Recipe Generator

This headless backend service leverages the power of Google's Gemini 1.5 Flash model to provide AI-powered recipe filtering. It fetches recipes from the Edamam database and uses the Gemini model to intelligently filter them based on a user's detailed health profile, ensuring that all recommendations are healthy and suitable for their specific needs.

## Features

*   **Personalized Recipe Recommendations:** Filters recipes based on user age, weight, height, and health concerns.
*   **Intelligent Health Analysis:** Uses the Gemini 1.5 Flash model for a nuanced nutritional assessment of recipes.
*   **Rich Recipe Database:** Integrates with the Edamam API to source a wide variety of recipes.
*   **Secure by Design:** All external API calls and secret key management are handled on the server-side.
*   **Headless Architecture:** Provides a clean, un-opinionated API for any frontend client to consume.

## [Architecture Overview](https.www.mermaidchart.com/app)
*   **Client (Frontend):** A user-facing application (web, mobile) that collects user health data and ingredients. It has no direct access to AI models or secret keys.
*   **Backend (This Project):** A Flask server that exposes API endpoints. It is responsible for:
    *   Authenticating requests from the frontend.
    *   Calling the Edamam API to fetch recipes.
    *   Calling the Google Gemini API to filter recipes based on health data.
    *   Managing all secret keys (`GEMINI_API_KEY`, `EDAMAM_APP_ID`, etc.) securely.

## Project Structure

```
vision-team/
├── app/
│   ├── config.py             
│   ├── __init__.py           
│   └── v1/
│       ├── __init__.py
│       ├── routes.py         
│       ├── services.py       
│       ├── schemas.py        
├── .env.example              
├── .env                      
├── requirements.txt          
└── run.py                    
```

## Backend Setup & Installation

### Prerequisites

*   Python 3.10 or higher
*   An account with [Google AI Studio](https://aistudio.google.com/) to get a `GEMINI_API_KEY`.
*   An account with [Edamam](https://developer.edamam.com/) to get an App ID and App Key.

### Step 1: Clone the repository

```bash
git clone https://github.com/your-username/nutri-ai.git
cd nutri-ai
```

### Step 2: Create & activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create your own `.env` file by copying the example.

```bash
cp .env.example .env
```

Now, edit the `.env` file and add your actual secret keys and credentials.

```dotenv
# Flask-specific keys
SECRET_KEY=generate-a-strong-random-secret-key
FLASK_ENV=development

# API key for securing your backend endpoints
X_API_KEY=a-secret-key-your-frontend-will-send

# Google AI API Key
GEMINI_API_KEY=your-google-ai-studio-api-key

# Edamam API Credentials
EDAMAM_APP_ID=your-edamam-app-id
EDAMAM_APP_KEY=your-edamam-app-key
EDAMAM_API_ENDPOINT=https://api.edamam.com/api/recipes/v2
```

### Step 5: Run the development server

```bash
python run.py
```

Your API is now running and accessible at `http://127.0.0.1:5000/`.
Swagger UI documentation will be available at `http://127.0.0.1:5000/docs/`.

## API Usage

All API calls must include the `X-API-Key` header for authentication.

### Filter Recipes

Send a `POST` request to `/v1/recipes/filter` with the user's profile and ingredients.

**Request Body:**

```json
{
  "user_profile": {
    "age": 30,
    "gender": "female",
    "weight": 65,
    "height": 170,
    "disease": "high cholesterol"
  },
  "ingredients": ["chicken", "broccoli", "quinoa"]
}
```

**Example (`curl`):**

```bash
curl -X POST http://127.0.0.1:5000/v1/recipes/filter \
-H "Content-Type: application/json" \
-H "X-API-Key: a-secret-key-your-frontend-will-send" \
-d '{
  "user_profile": {
    "age": 30, "gender": "female", "weight": 65,
    "height": 170, "disease": "high cholesterol"
  },
  "ingredients": ["chicken", "broccoli", "quinoa"]
}'
```

**Success Response (200 OK):**

```json
{
  "recipes": [
    {
      "label": "Healthy Chicken and Broccoli Bowl",
      "url": "http://example.com/recipe-url",
      "calories": 450,
      "yield": 4,
      "image": "http://example.com/image.jpg",
      "ingredientLines": ["1 lb chicken breast", "2 cups broccoli florets", "1 cup cooked quinoa"]
    }
  ]
}
```

## Important Notes

*   This backend is **headless**. It is designed to be consumed by a separate frontend application.
*   **Security:** Never commit your `.env` file or any other files containing secrets to version control.