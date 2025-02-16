from ancients.settings.base import *
DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, '/shared/ancients.sqlite3'),
        # it is not necessary to use an externally hosted database, the onboard sqlite file suffices
        'NAME': os.path.join(BASE_DIR, 'ancients.sqlite3'),
    }
}