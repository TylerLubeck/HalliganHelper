# Django settings for HalliganAvailability project.
import os
import errno
import logging
logger = logging.getLogger(__name__)


def get_secret_from_file(secret_name):
    """Fetch a secret from the file, return None if it doesn't exist

    Args:
        secret_name (str): the name of the file to read
        path_prefix (str): the directory the file lives in

    Returns:
        str or None: the secret, or None if not found
    """
    val = None
    try:
        with open(secret_name, 'r') as f:
            val = f.read().strip()
    except (OSError, IOError):
        logger.error('Failed to get secret from %s', path, exc_info=True)

    return val


def get_secret_from_env(secret_name):
    """Fetch a secret from an environment var, return None if it doesn't exist

    Args:
        secret_name (str): the name of the environment variable to read from

    Returns:
        str or None: the secret, or None if not found
    """
    val = os.environ.get(secret_name)
    if val is None:
        logger.error('Failed to find environment variable %s', secret_name)
    return val


def get_secret(secrets):
    """Fetch a secret from the first available location in `secrets`
    Args:
        secrets (List[str]): a list of places to look for secrets. 
            The secret is returned from the first place it is found.

            Entries in this list must be in one of the following forms:
                `file:<path_to_file>` - to look up the secret from a file
                `env:<env_var_name>` - to look up the secret from an env var
    Returns:
        str: The found secret

    Raises:
        Exception: If the secret isn't found in any of the locations
    """
    _secrets = secrets[:]
    val = None
    while val is None and len(_secrets):
        secret = _secrets.pop()
        if secret.startswith('file:'):
            val = get_secret_from_file(secret[5:])
        if secret.startswith('env:'):
            val = get_secret_from_env(secret[4:])

        if val:
            break

    if val is None:
        raise Exception(
            'Failed to get value for secrets %s', ','.join(secrets)
        )

    return val


PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = os.environ.get('DEBUG', 'False') == 'True'  # env vars are strings
ALLOWED_HOSTS = ['*']

SECRET_KEY = get_secret(['file:/var/secrets/secret_key', 'env:SECRET_KEY'])

MANAGERS = ADMINS = (
    ('Tyler Lubeck', 'Tyler@tylerlubeck.com'),
    ('Tyler Lubeck', 'halliganhelper@tylerlubeck.com'),
)

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
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True


# Use redis for session management

SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS_HOST = REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
SESSION_REDIS_PORT = REDIS_PORT = 6379
SESSION_REDIS_PASSWORD = REDIS_PASSWORD = get_secret(
    ['file:/var/secrets/redis_password', 'env:REDIS_PASSWORD']
)
SESSION_REDIS_PREFIX = 'session'

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
                'django.core.context_processors.request',
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

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'super_inlines',
    'django.contrib.admin',
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

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'
BROKER_URL = 'redis://redis:6379/0'
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
WS4REDIS_EXPIRE = 0  # Don't hold messages. You see it or you don't.
WS4REDIS_CONNECTION = {
    'password': REDIS_PASSWORD,
    'port': REDIS_PORT,
    'host': REDIS_HOST,
}


# This is a dummy database setup. You'll need to insert your own
# database name and passwords
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', ''),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': get_secret(['file:/var/secrets/db_password', 'env:DB_PASSWORD']),
        'HOST': 'db'
    }
}

EMAIL_HOST_USER = 'noreply@halliganhelper.com'
DEFAULT_FROM_EMAIL = 'support@halliganhelper.com'
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_PASSWORD = get_secret(['file:/var/secrets/email_password', 'env:EMAIL_PASSWORD'])

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static Assets
MEDIA_URL = '/media/'
MEDIA_ROOT = '/media'

STATIC_URL = '/static/'
STATIC_ROOT = '/assets'

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'assets'),
)

# Django Webpack Loader
WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': '/webpack-stats/webpack-stats.json',
    },
}

INSTALLED_APPS += (
    'webpack_loader',
)


# Django Rest Framework
INSTALLED_APPS += (
    'rest_framework',
    'djoser',  # DRF app for password resets
)

DJOSER = {
    'PASSWORD_RESET_CONFIRM_URL': '/password/reset/confirm/{uid}/{token}',
}

DEFAULT_RENDERER_CLASSES = (
    'rest_framework.renderers.JSONRenderer',
)

if DEBUG:
    DEFAULT_RENDERER_CLASSES += (
        'rest_framework.renderers.BrowsableAPIRenderer',
    )

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': DEFAULT_RENDERER_CLASSES,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}


LOG_FORMAT = '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': LOG_FORMAT,
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'halliganhelper.log',
            'formatter': 'verbose',
        },
        'authentication_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'halliganhelper-auth.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}
