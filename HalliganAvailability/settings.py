# Django settings for HalliganAvailability project.
import os

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ADMINS = (
    ('Tyler Lubeck', 'Tyler@tylerlubeck.com'),
    ('Tyler Lubeck', 'halliganhelper@tylerlubeck.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(os.path.dirname(__file__), 'templates').replace('\\', '/'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'ws4redis.context_processors.default',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'HalliganAvailability.urls'

# Using the one defined by Websocket-For-Redis below.
# WSGI_APPLICATION = 'HalliganAvailability.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'super_inlines',
    'django.contrib.admin',
    # 'django.contrib.admindocs',
    'tas',
    'registration',
    'django_extensions',
    'imagekit',
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

AUTH_USER_MODEL = 'tas.CustomUser'

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}

ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_OPEN = True

LOG_FORMAT = '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': LOG_FORMAT,
            'datefmt': '%d/%b/%Y %H:%M:%S'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'halliganhelper.log',
            'formatter': 'verbose'
        },
        'authentication_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'halliganhelper-auth.log',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False
        },
        'HalliganAvailability': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG'
        },
        'tas': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG'
        },
        'HalliganAvailability.authentication': {
            'handlers': ['console', 'authentication_file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'
BROKER_URL = 'redis://localhost:6379/0'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 10850}


ALLOWED_REGISTRATION_DOMAINS = ('tufts.edu', 'cs.tufts.edu')


# Websocket-for-Redis stuff

INSTALLED_APPS += (
    'ws4redis',
)

WEBSOCKET_URL = '/ws/'
WS4REDIS_PREFIX = 'hh'

WSGI_APPLICATION = 'ws4redis.django_runserver.application'
WS4REDIS_HEARTBEAT = '--heartbeat--'


# This is a dummy database setup. You'll need to insert your own
# database name and passwords
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'halliganhelper',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost'
    }
}

EMAIL_HOST_USER = 'halliganhelper@tylerlubeck.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# Static Assets
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = 'mediafiles/'
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'staticfiles')

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'assets'),
)

# Django Webpack Loader
WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(PROJECT_ROOT, 'webpack-stats.json'),
    },
}

INSTALLED_APPS += (
    'webpack_loader',
)
try:
    from secret import *
except ImportError:
    WS4REDIS_CONNECTION = {
        'password': ''
    }
    DEBUG = False
    EMAIL_HOST_PASSWORD = ''
    SECRET_KEY = 'secret_key'
    ALLOWED_HOSTS = ['*']

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

if DEBUG:
    pass
    # INSTALLED_APPS += (
    #     'debug_toolbar',
    # )

# Django Rest Framework
INSTALLED_APPS += (
    'rest_framework',
)

DEFAULT_RENDERER_CLASSES = (
    'rest_framework.renderers.JSONRenderer',
)

if DEBUG:
    DEFAULT_RENDERER_CLASSES += (
        'rest_framework.renderers.BrowsableAPIRenderer',
    )

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': DEFAULT_RENDERER_CLASSES
}
