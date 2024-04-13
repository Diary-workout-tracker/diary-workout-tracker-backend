import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

LOG_ERRORS_TO_FILE_LEVEL = "WARNING"
PATH_TO_LOGS = os.path.join(BASE_DIR, "logs/django.log")

LOGGING_SETTINGS = {
	"version": 1,
	"disable_existing_loggers": True,
	"formatters": {
		"formatter": {
			"()": "django.utils.log.ServerFormatter",
			"format": "[%(name)s %(asctime)s %(filename)s: %(lineno)d - %(funcName)s()] %(message)s",
			"datefmt": "%Y-%m-%d %H:%M:%S",
		}
	},
	"handlers": {
		"console": {
			"level": "DEBUG",
			"class": "logging.StreamHandler",
			"formatter": "formatter",
		},
		"file": {
			"level": LOG_ERRORS_TO_FILE_LEVEL,
			"class": "logging.handlers.TimedRotatingFileHandler",
			"filename": PATH_TO_LOGS,
			"formatter": "formatter",
			"when": "midnight",
			"backupCount": 30,
		},
	},
	"loggers": {
		"django": {
			"handlers": ("file",),
			"level": "DEBUG",
			"propagate": False,
		},
		"django.db.backends": {
			"handlers": ("console",),
			"level": "DEBUG",
			"propagate": False,
			"filters": ["require_debug_true"],
		},
	},
	"filters": {
		"require_debug_true": {
			"()": "django.utils.log.RequireDebugTrue",
		},
	},
}
