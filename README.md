# Blog API – Middleware (Django REST Framework)

A RESTful API backend for a blogging platform, built with Django REST Framework and PostgreSQL. This is the middleware layer of a three-tier enterprise application.

## Tech Stack

- Python / Django 5.2
- Django REST Framework
- PostgreSQL (production) / SQLite (development)
- JWT Authentication (djangorestframework-simplejwt)
- SendGrid (email / password reset)
- Cloudinary (profile image storage)
- WhiteNoise (static file serving)
- Gunicorn (production WSGI server)

## Technical Decisions

- **JWT over sessions** — stateless tokens suit a decoupled frontend/backend architecture; no server-side session storage required
- **PostgreSQL in production, SQLite in development** — SQLite keeps local setup dependency-free; `dj-database-url` handles the switch via a single env var
- **Cloudinary for media** — offloads image storage and transformation from the server; avoids serving user uploads through Django in production
- **SendGrid via django-anymail** — anymail provides a consistent Django email interface regardless of provider, keeping the code decoupled from the specific email service
- **WhiteNoise for static files** — eliminates the need for a separate CDN or web server for static assets in production

## Architecture

This API sits between the React frontend and the PostgreSQL database. It handles:

- Authentication and authorisation (JWT)
- Business logic and validation
- All database access (the frontend never touches the DB directly)

Apps are modular by domain:

- `accounts` – registration, login, profiles, password reset
- `posts` – blog post CRUD with status management
- `comments` – post-scoped comment CRUD

## Local Setup

### Prerequisites

- Python 3.12+
- pip

### Steps

~~~bash
git clone <repo-url>
cd Ada-ESE-1-BackEnd

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

python manage.py migrate
python manage.py runserver
~~~

The API will be available at `http://localhost:8000`.

## Environment Variables

See `.env.example` for all required variables.

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for development, `False` for production |
| `DATABASE_URL` | Database connection string |
| `SENDGRID_API_KEY` | SendGrid API key for email |
| `DEFAULT_FROM_EMAIL` | Sender email address |
| `FRONTEND_URL` | Frontend URL (used for CORS and password reset links) |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |

## API Endpoints

### Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register a new user |
| POST | `/api/auth/login/` | Login – returns JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| POST | `/api/auth/password-reset/` | Request password reset email |
| POST | `/api/auth/password-reset/confirm/<uid>/<token>/` | Confirm password reset |

### User

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/me/` | Get current user info |
| GET / PATCH | `/api/profile/` | View or update profile and avatar |

### Posts

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/posts/` | List published posts (+ own drafts if authenticated) |
| POST | `/api/posts/` | Create a post |
| GET | `/api/posts/<id>/` | Get a single post |
| PATCH | `/api/posts/<id>/` | Update a post (author only) |
| DELETE | `/api/posts/<id>/` | Delete a post (author only) |

### Comments

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/posts/<id>/comments/` | List comments on a post |
| POST | `/api/posts/<id>/comments/` | Add a comment (authenticated) |
| DELETE | `/api/posts/<id>/comments/<comment_id>/` | Delete a comment (author only) |

## Testing

~~~bash
pytest
~~~

Tests cover:

- User registration and login
- JWT token authentication
- Post visibility rules (drafts only visible to their author)
- Authorisation (non-authors receive 403)
- Comment scoping (comments only returned for their post)

Coverage report is printed automatically.
Tests achieve 90%+ coverage across the accounts, posts, and comments apps. Run pytest to see the full report.

## Deployment

Deployed on Render using `render.yaml`. The `build.sh` script handles migrations and static file collection on each deploy. `DATABASE_URL` is injected automatically from the linked PostgreSQL database.

Set all other environment variables in the Render dashboard.

Live API: `https://blog-api-jo4b.onrender.com`

## CI/CD

This repository uses GitHub Actions to run the test suite automatically on every push and pull request to `main`.

The workflow:
- Runs on Ubuntu with Python 3.12
- Installs all dependencies from `requirements.txt`
- Runs `pytest` using SQLite (no external database required in CI)
- Uses environment variables scoped to the CI environment — no secrets required

The workflow file is located at `.github/workflows/django.yml`.

## Security

- Passwords hashed using Django's built-in hasher; strength enforced via Django's built-in password validators
- JWT with short-lived access tokens and refresh token rotation
- All write endpoints require authentication
- Authors can only modify their own content (`IsAuthorOrReadOnly` permission class)
- Secrets managed via environment variables — never committed to version control

## AI Declaration

**Tool used:** Claude Code (Anthropic)

Claude Code was used in the following specific ways during development:

- **Deployment configuration** — assisted with writing the `render.yaml` and `build.sh` scripts, and debugging `ALLOWED_HOSTS` and `CORS` configuration for the Render deployment
- **CI/CD setup** — helped draft the GitHub Actions workflow (`django.yml`), which was reviewed and understood before being committed
- **Code review** — used to review the `IsAuthorOrReadOnly` permission class and password reset token flow for correctness; suggestions were evaluated and integrated manually
- **Debugging** — used to diagnose a `pytest` configuration issue with `DATABASE_URL` in the CI environment; the fix was understood and applied manually
- **README drafting** — used to help structure and draft this documentation, which was reviewed and edited to accurately reflect the actual implementation

All core application logic — models, views, serializers, authentication, and tests — was written independently. AI-assisted content was critically evaluated before inclusion. Any code generated or suggested by AI was read, understood, and manually integrated; nothing was accepted without review.
