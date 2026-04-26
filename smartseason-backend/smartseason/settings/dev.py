"""Development settings — verbose, permissive CORS for local dev."""
from .base import *  # noqa
DEBUG = True
ALLOWED_HOSTS = ["*"]
# Allow Vite (5173) and CRA (3000) by default
CORS_ALLOW_ALL_ORIGINS = True
