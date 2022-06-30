"""Use this for production"""

from .base import *

DEBUG = False
ALLOWED_HOSTS += ["137.184.7.33"]
WSGI_APPLICATION = "home.wsgi.prod.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "facial_recognition",
        "USER": "danielw",
        "PASSWORD": "qwert",
        "HOST": "localhost",
        "PORT": "",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

STATICFILES_STORAGE = "whitenoise.django.GzipManifestStaticFilesStorage"
STRIPE_PUBLISH_KEY = "pk_test_MaMJmdWrhGRr6EwcDQBWbYos"
STRIPE_SECRET_KEY = "sk_test_OSCEWCzNeKncTxZUbdlWqvyF"
