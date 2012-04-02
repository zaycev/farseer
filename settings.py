from options import DATABASE_CONFIG as db

DEBUG = False
TEMPLATE_DEBUG = DEBUG


def project_dir(dir_name):
	import os
	return os.path.join(os.path.dirname(__file__), dir_name).replace("\\", "//"),


ADMINS = (("Admin", "contact@test.org",),)
MANAGERS = ADMINS



DATABASES = {
    'default': {
        'ENGINE': db["pg"]["driver"],
        'NAME': db["pg"]["database"],
        'USER': db["pg"]["user"],
        'PASSWORD': db["pg"]["password"],
        'HOST': db["pg"]["host"],
        'PORT': db["pg"]["port"],
	}
}


SECRET_KEY = '+_43#jy2_6tzh%m*0ga&dlwu__)p0l083^g32!_ieo(jt#=j77'
TIME_ZONE = 'Asia/Yekaterinburg'
LANGUAGE_CODE = 'en-US'
SITE_ID = 1
USE_I18N = False
USE_L10N = False


ADMIN_MEDIA_PREFIX = '/www/admin/'
ADMIN_MEDIA = project_dir("www/admin/")


MEDIA_ROOT = project_dir("www")
MEDIA_URL = "/"


STATIC_ROOT = "/www/"
STATIC_URL = '/www/'
STATICFILES_DIRS = (
	project_dir("www")
)
STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	'django.contrib.staticfiles.finders.DefaultStorageFinder',
)



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
	project_dir("templates")
)


INSTALLED_APPS = (
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	"collector",
	"analyzer",
	"fortest",
)


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