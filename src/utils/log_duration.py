from __future__ import annotations

import logging
import time
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@contextmanager
def log_duration(label: str):
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        logger.info("%s took %.2fs", label, elapsed)
