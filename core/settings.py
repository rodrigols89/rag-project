import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (
    "django-insecure-y&vae53ge@imkp#e%8$q^elqwcvi+dcixxl^%a6e_5wpx(z@bl"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


##############################################################################
# Hosts/domain names that are valid for this site/project                    #
##############################################################################

allowed_hosts = os.getenv(
    "DJANGO_ALLOWED_HOSTS",
    "localhost,127.0.0.1",
)

if allowed_hosts == "*":
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = [
        host.strip()
        for host in allowed_hosts.split(",")
        if host.strip()
    ]

# Necessário para Django Test Client
if "testserver" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("testserver")


##############################################################################
# Application definition                                                     #
##############################################################################

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "users",
]


##############################################################################
# Middleware settings                                                        #
##############################################################################

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"


##############################################################################
# Templates settings                                                         #
##############################################################################

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


##############################################################################
# WSGI settings                                                              #
##############################################################################

WSGI_APPLICATION = "core.wsgi.application"


##############################################################################
# Database settings                                                          #
##############################################################################

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}


##############################################################################
# Password validation                                                        #
##############################################################################

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


##############################################################################
# Internationalization                                                       #
##############################################################################

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True


##############################################################################
# Static files (CSS, JavaScript, Images)                                     #
##############################################################################

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"


##############################################################################
# Media files                                                                #
##############################################################################

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
