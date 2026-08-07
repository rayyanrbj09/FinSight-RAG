"""
Centralized logging configuration for the FinSight application.

Features:
- Console and file logging with customizable log levels.
- Log rotation to manage log file sizes and backups.
- Seperate log files for different components of the application.
- Consistent log formatting across the application.
- Module specific loggers for better traceability.
"""

import logging
import logging.config
import os 
from logging.handlers import RotatingFileHandler

from core.config import settings

def setup_logging() -> None:
    """
    Configuring application-wide logging settings.
    Call this function at the start of the application to ensure consistent logging behavior.
    """

    os.makedirs(settings.LOG_DIR, exist_ok=True)
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "standard": {
                "format": (
                    "%(asctime)s | "
                    "%(levelname)-8s | "
                    "%(name)s | "
                    "%(filename)s:%(lineno)d | "
                    "%(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },

        "handlers": {

            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": settings.LOG_LEVEL,
            },

            "app_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": settings.LOG_FILE,
                "maxBytes": settings.LOG_MAX_BYTES,
                "backupCount": settings.LOG_BACKUP_COUNT,
                "formatter": "standard",
                "level": settings.LOG_LEVEL,
            },
        },

        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(settings.LOG_DIR, "error.log"),
            "maxBytes": settings.LOG_MAX_BYTES,
            "backupCount": settings.LOG_BACKUP_COUNT,
            "formatter": "standard",
            "level": "ERROR",
        },

        "root": {
            "handlers": ["console", "app_file", "error_file"],
            "level": settings.LOG_LEVEL,
        },

    }

    logging.config.dictConfig(logging_config)

def get_logger(name: str) -> logging.Logger:
    "returns a logger instance for the specified module name."
    return logging.getLogger(name)




