from soundcloud.settings.common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1', ]


ALLOWED_HOSTS = [
    '127.0.0.1',
]


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'waffle-team-10-rds.cf6av8nj1vlu.ap-northeast-2.rds.amazonaws.com',
        'PORT': 3306,
        'NAME': 'soundcloud',
        'USER': 'waffle-team-10',
        'PASSWORD': get_secret("DB_PASSWORD"),
    }
}
