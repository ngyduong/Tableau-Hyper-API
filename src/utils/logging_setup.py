from __future__ import annotations

import logging
import os
import sys
from logging.config import dictConfig


def setup_logging(app_name: str = "tableau-cli", level: str | None = None) -> None:
    """
    Configure logging once for the whole app.
    Call this at the start of main().
    """
    log_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,  # keep library loggers
            "formatters": {
                "standard": {
                    "format": (
                        "%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(message)s"
                    )
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": log_level,
                    "formatter": "standard",
                    "stream": sys.stdout,
                },
            },
            "root": {
                "level": log_level,
                "handlers": ["console"],
            },
        }
    )

    # Optional: make noisy libs quieter
    logging.getLogger("tableau_server_client").setLevel(
        max(logging.INFO, logging.getLevelName(log_level))
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)
