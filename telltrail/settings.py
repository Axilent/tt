"""
Django settings for telltrail project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

import dj_database_url

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*#uqees$3!ot7(*-u@mm12n2si5^qwcff=9+qdz9(fo&4m#1%!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG',False)

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'telltrail',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'telltrail.urls'

WSGI_APPLICATION = 'telltrail.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DB_ENGINE = os.environ.get('DB_ENGINE','django.db.backends.postgresql_psycopg2')
DB_NAME = os.environ.get('DB_NAME','telltrail')
DB_USER = os.environ.get('DB_USER','')
DB_PASSWORD = os.environ.get('DB_PASSWORD','')
DB_HOST = os.environ.get('DB_HOST','127.0.0.1')
DB_PORT = os.environ.get('DB_PORT','5432')

LOCAL_DB = os.environ.get('LOCALDB',None)

DATABASES = {}
if LOCAL_DB:
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
        }
    }
else:
    DATABASES['default'] = dj_database_url.config()

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
local_static = os.environ.get('LOCALSTATIC',None)
if not local_static:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    STATICFILES_STORAGE = DEFAULT_FILE_STORAGE
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME','telltrail-prototype')
    STATIC_HOST = os.environ.get('STATIC_HOST','//s3.amazonaws.com')
    STATIC_URL = '%s/%s/' % (STATIC_HOST,AWS_STORAGE_BUCKET_NAME)


SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
