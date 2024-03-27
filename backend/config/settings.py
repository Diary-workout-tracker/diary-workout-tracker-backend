import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

path_to_env = os.path.join(BASE_DIR, "..", "infra", ".env")

load_dotenv(path_to_env)


SECRET_KEY = os.getenv("SECRET_KEY", default="secret_key")

DEBUG = os.getenv("DEBUG", default=False)

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", default="127.0.0.1").split(",")

CSRF_TRUSTED_ORIGINS = [os.getenv("CSRF_TRUSTED_ORIGINS", default="http://127.0.0.1")]


INSTALLED_APPS = [
	"django.contrib.admin",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sessions",
	"django.contrib.messages",
	"django.contrib.staticfiles",
	"django.forms",
	# lib
	"rest_framework",
	"rest_framework.authtoken",
	"drf_spectacular",
	"storages",
	# app
	"api.apps.ApiConfig",
	"running.apps.RunningConfig",
	"users.apps.UsersConfig",
]

MIDDLEWARE = [
	"django.middleware.security.SecurityMiddleware",
	"django.contrib.sessions.middleware.SessionMiddleware",
	"django.middleware.common.CommonMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	"django.contrib.messages.middleware.MessageMiddleware",
	"django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
	{
		"BACKEND": "django.template.backends.django.DjangoTemplates",
		"DIRS": [os.path.join(BASE_DIR, "templates")],
		"APP_DIRS": True,
		"OPTIONS": {
			"context_processors": [
				"django.template.context_processors.debug",
				"django.template.context_processors.request",
				"django.contrib.auth.context_processors.auth",
				"django.contrib.messages.context_processors.messages",
			],
		},
	},
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
	"default": {
		"ENGINE": os.getenv("DB_ENGINE", default="django.db.backends.postgresql"),
		"NAME": os.getenv("POSTGRES_DB", default="postgres"),
		"USER": os.getenv("POSTGRES_USER", default="postgres"),
		"PASSWORD": os.getenv("POSTGRES_PASSWORD", default="postgres"),
		"HOST": os.getenv("DB_HOST", default="localhost"),
		"PORT": os.getenv("DB_PORT", default=5432),
		"PG_USER": os.getenv("PG_USER", default="user"),
		"TIME_ZONE": os.getenv("TIME_ZONE", default="Europe/Moscow"),
	}
}

AUTH_PASSWORD_VALIDATORS = [
	{
		"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
	},
	{
		"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
	},
	{
		"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
	},
	{
		"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
	},
]

AUTH_USER_MODEL = "users.User"

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = os.getenv("TIME_ZONE", default="Europe/Moscow")

USE_I18N = True

USE_TZ = True


# s3 storage settings
IS_AWS_ACTIVE = os.getenv("IS_AWS_ACTIVE", False) == "True"
if IS_AWS_ACTIVE is True:
	STORAGES = {
		"default": {
			"BACKEND": "storages.backends.s3.S3Storage",
			"OPTIONS": {
				"bucket_name": "running-app",
				"location": "media",
			},
		},
		"staticfiles": {
			"BACKEND": "django.core.files.storage.FileSystemStorage",
			"OPTIONS": {
				"location": "/static",
				"base_url": "/static/",
			},
		},
	}
	AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
	AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
	AWS_S3_ACCESS_KEY_ID = os.getenv("AWS_S3_ACCESS_KEY_ID")
	AWS_S3_SECRET_ACCESS_KEY = os.getenv("AWS_S3_SECRET_ACCESS_KEY")
	AWS_S3_SIGNATURE_VERSION = os.getenv("AWS_S3_SIGNATURE_VERSION")

	MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/media/"
else:
	MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATIC_URL = "/static/"
if DEBUG:
	STATICFILES_DIRS = (os.path.join(BASE_DIR, "static/"),)
else:
	STATIC_ROOT = os.path.join(BASE_DIR, "static")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

REST_FRAMEWORK = {
	"DEFAULT_PERMISSION_CLASSES": [
		"rest_framework.permissions.IsAuthenticated",
	],
	"DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
	"DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
	"DEFAULT_THROTTLE_CLASSES": [
		"rest_framework.throttling.UserRateThrottle",
		"rest_framework.throttling.AnonRateThrottle",
	],
	"DEFAULT_THROTTLE_RATES": {
		"user": "10000/day",
		"anon": "1000/day",
	},
}

SPECTACULAR_SETTINGS = {
	"TITLE": "API сервиса 100 дней бега",
	"DESCRIPTION": "Live докумениация сервиса",
	"VERSION": "1.0.0",
	"SERVE_INCLUDE_SCHEMA": False,
}

CACHES = {
	"default": {
		"BACKEND": "django.core.cache.backends.locmem.LocMemCache",
		"LOCATION": "diary-localmemcache",
	}
}

# 100 years token lifetime

SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": timedelta(weeks=52 * 100)}

# access restore code

ACCESS_RESTORE_CODE_TTL_SECONDS = 300

ACCESS_RESTORE_CODE_THROTTLING = {
	"duration": timedelta(minutes=10),
	"num_requests": 5,
	"cooldown": timedelta(minutes=5),
}

# email send
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.yandex.ru")
EMAIL_PORT = os.getenv("EMAIL_PORT", 465)
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "True")


# LOGGING = LOGGING_SETTINGS
