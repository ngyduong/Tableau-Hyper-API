from __future__ import annotations

import argparse
import logging

from src.utils.log_duration import log_duration
from src.wrapper.config import ConfigWrapper
from src.wrapper.tableau_wrapper import TableauClient

logger = logging.getLogger(__name__)


def main(tsc: TableauClient, cfg: ConfigWrapper, args: argparse.Namespace) -> None:
    logger.info("Starting script: hyper_api_create_extract")

    with log_duration("hyper_api_create_extract"):
        # ---- ALL your script logic goes here ----
        print("hyper_api_create_extract' started")
        # ----------------------------------------

    logger.info("Script finished: hyper_api_create_extract")
