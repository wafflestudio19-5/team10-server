"""
Django settings for soundcloud project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/

Quick-start development settings - unsuitable for production
See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/
"""

import os
from pathlib import Path
import json
import datetime
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Keep Secret Key Secret

SECRET_FILE = os.path.join(BASE_DIR, "secrets.json")

with open(SECRET_FILE) as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)


SECRET_KEY = get_secret("SECRET_KEY")

# Settings for S3 bucket

AWS_ACCESS_KEY = get_secret("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = get_secret("AWS_SECRET_ACCESS_KEY")
S3_REGION_NAME = "ap-northeast-2"
S3_BUCKET_NAME = "django-team-10-media"
S3_BASE_URL = "https://" + S3_BUCKET_NAME + ".s3." + S3_REGION_NAME + ".amazonaws.com/"
S3_MUSIC_TRACK_DIR = "media/music/track/"
S3_IMAGES_SET_DIR = "media/images/set/"
S3_IMAGES_TRACK_DIR = "media/images/track/"
S3_IMAGES_USER_PROFILE_DIR = "media/images/user/profile/"
S3_IMAGES_USER_HEADER_DIR = "media/images/user/header/"

# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    'rest_framework_jwt',
    'rest_framework.authtoken',
    'drf_spectacular',
    'django_extensions',
    'guardian',
    'user.apps.UserConfig',
    'track',
    'set',
    'comment',
    'tag',
    'reaction',
    'utility',
    'haystack',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'soundcloud.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'soundcloud.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = STATIC_DIR

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Rest Framework settings

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),

    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'soundcloud.utils.CustomPagination',
    'PAGE_SIZE': 10
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # this is default
    'guardian.backends.ObjectPermissionBackend',
    # 'user.socialaccount.GoogleBackend',   
)

# JWT Authorization

JWT_AUTH = {
    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_ALGORITHM': 'HS256',
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(hours=12),
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=3),
}

# CORS
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
# CORS_ORIGIN_WHITELIST = (
#     "https://www.soundwaffle.com"
# )

# Custom User Model
AUTH_USER_MODEL = 'user.User'

SITE_ID = 1

SPECTACULAR_SETTINGS = {
    'TITLE': 'SoundWaffle API',
    'DESCRIPTION': 'Soundwaffle API Document',
    'VERSION': '0.1.0',
    'CONTACT': {
        'name': 'WaffleStudio Rookies 19.5 team-10-server',
        'url': 'https://github.com/wafflestudio19-5/team10-server',
    },
    'SWAGGER_UI_SETTINGS': {
        'dom_id': '#swagger-ui',
        'layout': 'BaseLayout',
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'filter': True,
    },
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,
    'COMPONENT_SPLIT_REQUEST': False,
}

# redis cache
# ex) sudo yum install redis / sudo systemctl start redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# for Sociallogin
SOCIAL_PASSWORD = "socialpassword"


WHOOSH_INDEX = os.path.join(BASE_DIR, 'whoosh_index')

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': WHOOSH_INDEX,
    },
}
