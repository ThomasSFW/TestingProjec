import os

from datetime import timedelta
from django.views.decorators.cache import cache_page
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(i#*06f#keydy_fh17bf=$0f6v)^wr^l7*u4gq42m*sztu#2_m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['127.0.0.1','localhost','20.205.17.43','infinyrealty.zenwhiz.online']
#SESSION_COOKIE_SAMESITE = 'None'
#SESSION_COOKIE_SECURE = True

# SSL settings
SESSION_COOKIE_SECURE = True  # Only send session cookies over HTTPS
CSRF_COOKIE_SECURE = True  # Only send CSRF cookies over HTTPS

# Security settings
SECURE_BROWSER_XSS_FILTER = True  # Enable XSS filtering
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME-sniffing
SECURE_SSL_REDIRECT = True  # Redirect all HTTP to HTTPS
SECURE_HSTS_SECONDS = 3600  # Enable HSTS for 1 hour
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Apply HSTS to subdomains
SECURE_HSTS_PRELOAD = True  # Allow your site to be included in the preload list

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Configure for reverse proxy

#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    #'adminlte3',
    #'adminlte2',
    #'adminlte3_theme',
    'django.contrib.admin',
    'django.contrib.auth',
    #'django.contrib.sites',
    #'djnago.contrib.sitemaps',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
	'InfinyRealty_app',
	#'InfinyRealty_app.apps.InfinyRealtyAppConfig',
]

INSTALLED_APPS += [
    "watermarker",
]

SITE_ID=1
 
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'InfinyRealty_app.redirect_https.RedirectToHttpsMiddleware',
    #'InfinyRealty_app.LoginCheckMiddleWare.LoginCheckMiddleWare',
    # 'django_auth_adfs.middleware.LoginRequiredMiddleware',
    # 'django.middleware.activeuser_middleware.ActiveUserMiddleware',
]

MIDDLEWARE_CLASSES = (
    'django_ssl_auth.SSLClientAuthMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
)

#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#        'LOCATION': 'default-cache'
#    }
#}
CACHES = {}
CACHE_MIDDLEWARE_SECONDS = 0
# Number of seconds of inactivity before a user is marked offline
USER_ONLINE_TIMEOUT = 300
SQL_SERVER_TIMEOUT = 60
# Number of seconds that we will keep track of inactive users for before 
# their last seen is removed from the cache
#USER_LASTSEEN_TIMEOUT = 60 * 60 * 24 * 7
HTML_MINIFY = False

ROOT_URLCONF = 'InfinyRealty_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [],
        'DIRS': [os.path.join(BASE_DIR, 'templates').replace('\\', '/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [                
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins': [
                'InfinyRealty_app.templatetags.custom_template_tags',
            ],
        },
    },
]

WSGI_APPLICATION = 'InfinyRealty_system.wsgi.application'

# zenSystem database
AUTH_HOST = "infinyrealty\SQLEXPRESS"
#AUTH_HOST = "178.212.35.254"
AUTH_USER = "sa"
AUTH_PASSWORD = "P@ssw0rd"

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

#EMAIL_HOST_USER = 'infinyrealty1@gmail.com'
#EMAIL_HOST_PASSWORD = 'ztsq mwzv rwdb kwru'
EMAIL_HOST_USER = 'infinyrealtyltd@gmail.com'
EMAIL_HOST_PASSWORD = 'pikf dpoz keci glwa'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
#https://support.google.com/accounts/answer/185833

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
#SESSION_COOKIE_AGE = 1200 # 1 minutes

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'infinyrealty': {
        'ENGINE': 'mssql',
        'NAME': 'InfinyRealty',
        'USER': AUTH_USER,
        'PASSWORD': AUTH_PASSWORD,
        'HOST': AUTH_HOST,
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'timeout': SQL_SERVER_TIMEOUT,
        },
    },

}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Registering Custom Backend "EmailBackEnd"
AUTHENTICATION_BACKENDS = [
    'InfinyRealty_app.EmailBackEnd.EmailBackEnd',
    'django_ssl_auth.SSLClientAuthBackend',
    # 'django_auth_adfs.backend.AdfsAuthCodeBackend',
    # 'django_auth_adfs.backend.AdfsAccessTokenBackend',
]

#For Custom USER
AUTH_USER_MODEL = "InfinyRealty_app.CustomUser"
AUTOCREATE_VALID_SSL_USERS = True

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
#STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

PROPERTY_ROOT = os.path.join(BASE_DIR, 'static\\dist\\img-web\\property-cms')
PATH_MAIN = "C:\\Website\\InfinyRealty\\static\\dist\\img-web\\main\\"
PATH_PROPERTY = "C:\\Website\\InfinyRealty\\static\\dist\\img-web\\property-cms\\"
PATH_FLOORPLAN = "C:\\Website\\InfinyRealty\\static\\dist\\img-web\\floorplan-cms\\"
PATH_PROPERTY_NEW = "C:\\Website\\InfinyRealty\\static\\dist\\img-web\\propertynew-cms\\"
PATH_FLOORPLAN_NEW = "C:\\Website\\InfinyRealty\\static\\dist\\img-web\\floorplannew-cms\\"
PATH_DOCUMENT = "C:\\Website\\InfinyRealty\\static\\dist\\img-web\\document-cms\\"
PATH_PROPERTY_FOREIGN = "C:\\Website\\InfinyRealty\\static\\dist\\img-web\\propertyforeign-cms\\"
PATH_FLOORPLAN_FOREIGN = "C:\\Website\\InfinyRealty\\static\\dist\\img-web\\floorplanforeign-cms\\"
PATH_ODDSHEET_TEMPLATE = "C:\\Website\\InfinyRealty\\static\\dist\\img-web\\oddsheet"
PATH_OFFER_TEMPLATE = "C:\\Website\\InfinyRealty\\static\\dist\\img-web\\offer"
PATH_OTHER = "C:\\Website\\InfinyRealty\\static\\other\\"