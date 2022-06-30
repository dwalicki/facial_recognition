"""Use this for development"""

from .base import *

ALLOWED_HOSTS += ["*"]
DEBUG = True

WSGI_APPLICATION = "home.wsgi.dev.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

CORS_ORIGIN_WHITELIST = ("http://localhost:3000",)

STRIPE_PUBLISH_KEY = "pk_test_MaMJmdWrhGRr6EwcDQBWbYos"
STRIPE_SECRET_KEY = "sk_test_OSCEWCzNeKncTxZUbdlWqvyF"
STRIPE_PLAN_ID = "price_1L6Oz9GV9KJMsjyEcKkidLeK"
