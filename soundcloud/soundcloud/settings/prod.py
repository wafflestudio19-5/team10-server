from soundcloud.settings.common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1', ]


ALLOWED_HOSTS = [
    'api.soundwaffle.com',
    '127.0.0.1',
]


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'django-team-10-database.cdfa0hitpoet.ap-northeast-2.rds.amazonaws.com',
        'PORT': 3306,
        'NAME': 'soundcloud',
        'USER': 'waffle-team-10',
        'PASSWORD': get_secret("DB_PASSWORD"),
    }
}

BASE_BACKEND_URL = 'https://api.soundwaffle.com'
BASE_FRONTEND_URL = 'https://www.soundwaffle.com'