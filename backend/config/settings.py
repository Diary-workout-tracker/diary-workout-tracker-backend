import os
from datetime import timedelta
from distutils.util import strtobool
from pathlib import Path

from dotenv import load_dotenv

from .logs import LOGGING_SETTINGS

BASE_DIR = Path(__file__).resolve().parent.parent

path_to_env = os.path.join(BASE_DIR, "..", "infra", ".env")

load_dotenv(path_to_env)


SECRET_KEY = os.getenv("SECRET_KEY", default="secret_key")

DEBUG = strtobool(os.getenv("DEBUG", default="False"))

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

TIME_ZONE = "UTC"

DATABASES = {
	"default": {
		"ENGINE": os.getenv("DB_ENGINE", default="django.db.backends.postgresql"),
		"NAME": os.getenv("POSTGRES_DB", default="postgres"),
		"USER": os.getenv("POSTGRES_USER", default="postgres"),
		"PASSWORD": os.getenv("POSTGRES_PASSWORD", default="postgres"),
		"HOST": os.getenv("DB_HOST", default="localhost"),
		"PORT": os.getenv("DB_PORT", default=5432),
		"PG_USER": os.getenv("PG_USER", default="user"),
		"TIME_ZONE": TIME_ZONE,
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

USE_I18N = True

USE_TZ = True


# s3 storage settings
IS_AWS_ACTIVE = strtobool(os.getenv("IS_AWS_ACTIVE", default="False"))
if IS_AWS_ACTIVE:
	STORAGES = {
		"default": {
			"BACKEND": "config.storage.S3MediaStorage",
		},
		"staticfiles": {
			"BACKEND": "config.storage.StaticS3Boto3Storage",
		},
	}

	STATICFILES_LOCATION = "static"
	MEDIAFILES_LOCATION = "media"

	MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
	MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
	MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")
	MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
	MINIO_ACCESS_URL = os.getenv("MINIO_ACCESS_URL")
	MINIO_STORAGE_USE_HTTPS = os.getenv("MINIO_STORAGE_USE_HTTPS", False) == "True"
	MINIO_S3_SECURE_URLS = os.getenv("MINIO_S3_SECURE_URLS", False) == "True"

	AWS_ACCESS_KEY_ID = MINIO_ACCESS_KEY
	AWS_SECRET_ACCESS_KEY = MINIO_SECRET_KEY
	AWS_STORAGE_BUCKET_NAME = MINIO_BUCKET_NAME
	AWS_S3_ENDPOINT_URL = MINIO_ENDPOINT
	AWS_S3_FILE_OVERWRITE = os.getenv("AWS_S3_FILE_OVERWRITE", False) == "True"
	AWS_S3_SIGNATURE_VERSION = os.getenv("AWS_S3_SIGNATURE_VERSION")
	AWS_S3_USE_SSL = os.getenv("AWS_S3_USE_SSL", False) == "True"
	AWS_S3_SECURE_URLS = os.getenv("AWS_S3_SECURE_URLS", False) == "True"
	AWS_S3_URL_PROTOCOL = os.getenv("AWS_S3_URL_PROTOCOL", "http:")

MEDIA_URL = "/media/"
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")


if DEBUG is True:
	STATICFILES_DIRS = (os.path.join(BASE_DIR, "static/"),)
else:
	STATIC_ROOT = os.path.join(BASE_DIR, "static")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

REST_FRAMEWORK = {
	"DATETIME_INPUT_FORMATS": ["%Y-%m-%d %H:%M:%S"],
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
		"anon": "2000/day",
	},
	"EXCEPTION_HANDLER": "api.v1.exceptions.custom_exception_handler",
}

SPECTACULAR_SETTINGS = {
	"TITLE": "API сервиса 100 дней бега",
	"DESCRIPTION": "Live докумениация сервиса",
	"VERSION": "1.0.0",
	"SERVE_INCLUDE_SCHEMA": False,
}

REDIS_LOCATION = f"redis://{os.getenv('REDIS_HOST', default='localhost')}:{os.getenv('REDIS_PORT', default='6379')}"

CELERY_BROKER_URL = f"{REDIS_LOCATION}/0"
CELERY_RESULT_BACKEND = f"{REDIS_LOCATION}/0"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 5 * 60
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"
CELERY_TIMEZONE = os.getenv("TIME_ZONE", default="Europe/Moscow")

CACHES = {
	"default": {
		"BACKEND": "django.core.cache.backends.redis.RedisCache",
		"LOCATION": REDIS_LOCATION,
	}
}


# 100 years token lifetime

SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": timedelta(weeks=52 * 100)}

# access restore code

ACCESS_RESTORE_CODE_TTL_SECONDS = 300

ACCESS_RESTORE_CODE_THROTTLING = {
	"duration": timedelta(minutes=10),
	"num_requests": 6,
	"cooldown": timedelta(minutes=5),
}

# email send
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.yandex.ru")
EMAIL_PORT = os.getenv("EMAIL_PORT", 465)
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "True")

# logging
IS_LOGGING = strtobool(os.getenv("IS_LOGGING", default="False"))
if IS_LOGGING:
	LOGGING = LOGGING_SETTINGS
else:
	LOGGING = None
