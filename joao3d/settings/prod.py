from .base import *
import os

DEBUG = True

ALLOWED_HOSTS = ['localhost', '192.168.0.42']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# Em produção, menos verboso no console
LOGGING['handlers']['console']['level'] = 'WARNING'
LOGGING['handlers']['console']['formatter'] = 'simple'

# Nível menos verboso para a app objetos
LOGGING['loggers']['objetos']['level'] = 'INFO'