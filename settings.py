
import os
from options import DATABASE_CONFIG as db

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
	("Admin", "contact@test.org"),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': db["web"]["driver"],
        'NAME': db["web"]["database"],
        'USER': db["web"]["user"],
        'PASSWORD': db["web"]["password"],
        'HOST': db["web"]["host"],
        'PORT': db["web"]["port"],
#		'OPTIONS': {
#			'autocommit': True,
#			}
	}
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Yekaterinburg'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru-ru'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
ADMIN_MEDIA_PREFIX = '/www/admin/'
ADMIN_MEDIA = os.path.join(os.path.dirname(__file__), 'www/admin/').replace('\\', '//')

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'www').replace('\\', '//')
MEDIA_URL = "/"

STATIC_ROOT = "/"
STATIC_URL = '/www/'
STATICFILES_DIRS = [os.path.join(os.path.dirname(__file__), 'www').replace('\\', '//')]


STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
SECRET_KEY = '+_43#jy2_6tzh%m*0ga&dlwu__)p0l083^g32!_ieo(jt#=j77'
TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
 )
MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.auth.middleware.RemoteUserMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
)


ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
	os.path.join(os.path.dirname(__file__), 'templates').replace('\\', '//'),
)

INSTALLED_APPS = (
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
#	'web',
	"collector",
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
