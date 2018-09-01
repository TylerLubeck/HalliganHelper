# This is merely a template for the secret.py file that should contain all of
# your secret or device specific settings.


DEBUG = False
EMAIL_HOST_PASSWORD = 'INSERT_EMAIL_PASSWORD_HERE'
SECRET_KEY = 'INSERT_SECRET_KEY_HERE'
ALLOWED_HOSTS = ['*']

# This is a dummy database setup. You'll need to insert your own
# database name and passwords
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'halliganhelper',
        'USER': 'halliganhelper',
        'PASSWORD': 'halliganhelper',
        'HOST': 'localhost'
    }
}


WS4REDIS_CONNECTION = {
    'password': 'some_complicated_password'
}
