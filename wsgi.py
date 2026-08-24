"""Production WSGI entry point.

Use this module with Gunicorn instead of running app.py directly.
"""
import os

from app import app

# Override the development fallback before serving requests.
secret = os.getenv("SECRET_KEY")
if not secret or len(secret) < 32:
    raise RuntimeError("SECRET_KEY must be set to a random value of at least 32 characters")

app.config["SECRET_KEY"] = secret
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("FLASK_ENV", "production") == "production"

application = app
