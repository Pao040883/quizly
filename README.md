# Quizly Backend

Django REST API Backend for the Quizly quiz application with AI-powered quiz generation from YouTube videos.

## 📋 Requirements

### System Requirements
- Python 3.10+
- **FFMPEG** (globally installed) - **REQUIRED** for Whisper AI
- Git

### FFMPEG Installation

#### Windows
1. Download from https://www.gyan.dev/ffmpeg/builds/
2. Extract the file
3. Add the `bin` folder to your PATH environment variable
4. Test with: `ffmpeg -version`

#### macOS
```bash
brew install ffmpeg
```

#### Linux
```bash
sudo apt update
sudo apt install ffmpeg
```

## 🚀 Installation

### 1. Clone Repository
```bash
git clone https://github.com/Pao040883/quizzly.git
cd quizzly
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API Key
1. Go to: https://aistudio.google.com/app/apikey
2. Create a free API key
3. Open `core/settings.py`
4. Enter your API key:
```python
GEMINI_API_KEY = 'your_api_key_here'
```

### 5. Run Database Migrations
```bash
python manage.py migrate
```

### 6. Download Whisper AI Model (REQUIRED)
**⚠️ Important:** This step is mandatory before creating any quizzes!
```bash
python manage.py download_whisper
```
This will download the Whisper base model (~140 MB). This is a one-time process that takes less than 1 minute depending on your internet connection. The model is cached locally and will be instantly available for all future quiz creations.

**Note:** The application uses the 'base' model for optimal balance between performance and accuracy.

### 7. Create Admin User (optional)
```bash
python manage.py createsuperuser
```

### 8. Start Server
```bash
python manage.py runserver
```

The API is now running at: `http://localhost:8000`

## 📚 API Endpoints

### Authentication Endpoints

#### POST `/api/register/`
Registers a new user.

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password",
  "confirmed_password": "your_password",
  "email": "your_email@example.com"
}
```

**Response (201):**
```json
{
  "detail": "User created successfully!"
}
```

#### POST `/api/login/`
Logs in the user and sets auth cookies.

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response (200):**
```json
{
  "detail": "Login successfully!",
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "your_email@example.com"
  }
}
```

#### POST `/api/logout/`
Logs out the user and deletes all tokens.

**Authentication:** Required

**Response (200):**
```json
{
  "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
}
```

#### POST `/api/token/refresh/`
Refreshes the access token using the refresh token.

**Response (200):**
```json
{
  "detail": "Token refreshed",
  "access": "new_access_token"
}
```

### Quiz Endpoints

#### POST `/api/createQuiz/`
Creates a new quiz based on a YouTube URL.

**Authentication:** Required

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=example"
}
```

**Response (201):**
```json
{
  "id": 1,
  "title": "Quiz Title",
  "description": "Quiz Description",
  "created_at": "2023-07-29T12:34:56.789Z",
  "updated_at": "2023-07-29T12:34:56.789Z",
  "video_url": "https://www.youtube.com/watch?v=example",
  "questions": [
    {
      "id": 1,
      "question_title": "Question 1",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option A",
      "created_at": "2023-07-29T12:34:56.789Z",
      "updated_at": "2023-07-29T12:34:56.789Z"
    }
  ]
}
```

#### GET `/api/quizzes/`
Retrieves all quizzes of the authenticated user.

**Authentication:** Required

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Quiz Title",
    "description": "Quiz Description",
    "created_at": "2023-07-29T12:34:56.789Z",
    "updated_at": "2023-07-29T12:34:56.789Z",
    "video_url": "https://www.youtube.com/watch?v=example",
    "questions": [...]
  }
]
```

#### GET `/api/quizzes/{id}/`
Retrieves a specific quiz.

**Authentication:** Required

**Response (200):** Quiz object (see above)

#### PATCH `/api/quizzes/{id}/`
Updates individual fields of a quiz.

**Authentication:** Required

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated Description"
}
```

**Response (200):** Updated quiz object

#### DELETE `/api/quizzes/{id}/`
Deletes a quiz permanently.

**Authentication:** Required

**Response (204):** No content

## 🔒 Authentication

The API uses JWT authentication with HTTP-only cookies:
- `access_token`: Valid for 60 minutes
- `refresh_token`: Valid for 7 days
- Tokens are automatically blacklisted on logout

## 🛠️ Technologie-Stack

- **Django 5.1+** - Web Framework
- **Django REST Framework 3.16+** - REST API
- **djangorestframework-simplejwt 5.4+** - JWT Authentication with Blacklisting
- **django-cors-headers 4.6+** - CORS Support
- **OpenAI Whisper (tiny model)** - Audio Transcription
- **Google Gemini Flash 2.5** - AI-powered Quiz Generation
- **yt-dlp 2024.12+** - YouTube Audio Download
- **SQLite** - Database
- **Coverage 7.6+** - Code Coverage Testing
- **Flake8 7.0+** - PEP-8 Linting

## 📁 Projektstruktur (Clean Code)

```
backend/
├── core/                          # Django Project Settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── authentication/                # Authentication App
│   ├── api/                       # API Layer
│   │   ├── views.py              # API Endpoints (Login, Logout, Register)
│   │   ├── serializers.py        # Data Validation & Serialization
│   │   └── urls.py               # URL Routing
│   ├── utils.py                  # Helper Functions (Cookies, Responses)
│   ├── authentication.py         # Custom JWT Authentication
│   ├── models.py                 # User Models (if needed)
│   ├── admin.py                  # Admin Configuration
│   └── tests.py                  # 19 Comprehensive Tests
│
├── quizzes/                       # Quizzes App
│   ├── api/                       # API Layer
│   │   ├── views.py              # API Endpoints (Create, List, Detail)
│   │   ├── serializers.py        # Quiz & Question Serializers
│   │   └── urls.py               # URL Routing
│   ├── functions.py              # Business Logic (YouTube, Whisper, Gemini)
│   ├── utils.py                  # Helper Functions (DB Operations)
│   ├── models.py                 # Quiz & Question Models
│   ├── admin.py                  # Admin Configuration with Inlines
│   ├── tests.py                  # 29 Comprehensive Tests
│   └── management/
│       └── commands/
│           └── download_whisper.py  # Whisper Model Download Command
│
├── media/
│   └── temp_audio/               # Temporary Audio Files
├── manage.py
└── requirements.txt
```

### Architecture Principles

**Clean Code Compliance:**
- ✅ All functions ≤ 14 lines (39 functions total)
- ✅ Separation of Concerns (API / Business Logic / Utils)
- ✅ PEP-8 compliant (0 flake8 violations)
- ✅ 96% code coverage (48 tests, 100% pass rate)

**Layered Structure:**
- `api/` - API endpoints, request/response handling
- `functions.py` - Business logic (YouTube, AI, processing)
- `utils.py` - Reusable helper functions
- `models.py` - Database models
- `tests.py` - Comprehensive test suites

## 🔧 Configuration

### CORS Settings
Allowed origins can be adjusted in `core/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5500',
    'http://127.0.0.1:5500',
    'http://localhost:3000',
]
```

### JWT Settings
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

## 📝 Admin Panel

The Admin Panel is available at: `http://localhost:8000/admin/`

Features:
- User management
- Quiz management with inline questions
- Edit and add questions
- Search and filter functions

## 🐛 Troubleshooting

### FFMPEG not found
Make sure FFMPEG is correctly installed and in your PATH:
```bash
ffmpeg -version
```

### Gemini API Key Error
Check if the API key is entered in `settings.py`:
```python
GEMINI_API_KEY = 'your_api_key_here'
```

### CORS Errors
Add your frontend URL to `CORS_ALLOWED_ORIGINS`.

## 📄 License

This project is part of the Developer Akademie Backend Course.

## 👨‍💻 Development

### Code Quality Standards

**PEP-8 Compliance:**
```bash
flake8 . --exclude=migrations,venv,__pycache__,.git
```
Expected: 0 violations ✅

**Test Suite:**
```bash
# Run all tests
python manage.py test authentication quizzes

# Expected: 48 tests, 100% pass rate
```

**Code Coverage:**
```bash
# Run tests with coverage
coverage run --source='.' manage.py test authentication quizzes

# Generate coverage report
coverage report

# Expected: 96%+ coverage
```

**Code Style Guidelines:**
- ✅ All functions ≤ 14 lines
- ✅ PEP-8 compliant
- ✅ Descriptive variable names (snake_case)
- ✅ Docstrings for all functions
- ✅ Type hints where appropriate
- ✅ Clear separation of concerns (API / Business Logic / Utils)

### Project Metrics
- **Total Functions:** 39
- **Test Coverage:** 96% (765 statements, 28 untested)
- **Tests:** 48 (19 authentication + 29 quizzes)
- **PEP-8 Violations:** 0
- **Max Function Length:** 14 lines

## 📞 Support

For questions or issues, create an issue in the repository or contact the developer.
