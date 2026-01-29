from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Em desenvolvimento, queremos ver mais detalhes no console
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['handlers']['console']['formatter'] = 'verbose'

# Nível mais verboso para a app objetos
LOGGING['loggers']['objetos']['level'] = 'DEBUG'