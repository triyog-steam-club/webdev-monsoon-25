> Author: [Sitanshu Shrestha](https://github.com/itssitanshu)  
> Developed for STEAM Club's Web-Development Competition. Team: Shivansu Shrestha, Aarush Bhandari, John Khadka   
>   

# Jhon Team API

Author: [Sitanshu Shrestha](https://github.com/itssitanshu)
Developed for STEAM Club's Web-Development Competition.
Team: Kushal Kumar Bhujel, Bishwasta Marasini, Subhadaya Bhatta

## Features

* **User Management:** Create and manage users.
* **Question Paper Management:** Create, list, and manage question papers tied to users.
* **AI Question Generation:** Regenerate questions or generate new questions from existing papers using Google Gemini AI.
* **Structured API Docs:** OpenAPI specs via Flasgger Swagger UI.
* **Modular Architecture:** Backend as a REST API with clear separation of routes, schemas, and services.


## Project Structure

```
jhon-team/
├── app
│   ├── config.py
│   ├── __init__.py
│   └── v1
│       ├── docs
│       │   ├── chat_history.yml
│       │   ├── chat_send.yml
│       │   └── sentiment_analytics.yml
│       ├── __init__.py
│       ├── models.py
│       ├── routes.py
│       ├── schemas.py
│       └── services.py
├── .env.example
├── .env
├── requirements.txt
└── run.py
```

## Backend Setup & Installation (Local with pip)

### Prerequisites

* Python 3.10 or higher
* pip (comes with Python)

### Step 1: Clone the repo

```bash
git clone https://github.com/your-org/jhon-team.git
cd jhon-team
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

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your secret keys:

```dotenv
SECRET_KEY='change-this-to-a-very-long-and-random-string-for-security'
SQLALCHEMY_DATABASE_URI='sqlite:///app.db'
GEMINI_API_KEYS='first-key,second-key,third-key'
FLASK_ENV=development
```

* Generate a secure `SECRET_KEY` (e.g., use Python `secrets.token_urlsafe(32)`)
* `SQLALCHEMY_DATABASE_URI` sqlite:///app.db is best
* `GEMINI_API_KEYs` are your Google AI Studio API key for Gemini

### Step 6: Run the server

```bash
python run.py
```

API available at:

```
http://127.0.0.1:5001/api/v1/
```

Swagger UI docs at:

```
http://127.0.0.1:5001/docs/
```

---

## Usage

### Create a user

```bash
curl -X POST http://127.0.0.1:5000/api/v1/users \
 -H "Content-Type: application/json" \
 -d '{"username":"teacher_jane"}'
```

### Create a question paper for a user

```bash
curl -X POST http://127.0.0.1:5000/api/v1/users/1/papers \
 -H "Content-Type: application/json" \
 -d '{"title":"World History Midterm", "content":"What caused World War I? Who led the Soviet Union during the Cuban Missile Crisis?"}'
```

### List question papers of a user

```bash
curl http://127.0.0.1:5000/api/v1/users/1/papers
```

### Regenerate a question with AI

```bash
curl -X PUT http://127.0.0.1:5000/api/v1/papers/1/questions/2/regenerate \
 -H "Content-Type: application/json" \
 -d '{"extra_prompt":"Make it easier for 5th graders."}'
```

### Generate a new question from paper context

```bash
curl -X POST http://127.0.0.1:5000/api/v1/papers/1/questions/generate
```


## Notes

* This backend is **headless**; build your own frontend or integrate with any client.
* Store `.env` safely, **never commit secrets**.
* For production, use a WSGI server (like Gunicorn) and HTTPS.
