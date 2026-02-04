from __future__ import annotations

import argparse
import logging

from src.utils.log_duration import log_duration
from src.wrapper.config import ConfigWrapper
from src.wrapper.tableau_wrapper import TableauClient

logger = logging.getLogger(__name__)


def main(cfg: ConfigWrapper, args: argparse.Namespace) -> None:
    """
    Publish a Hyper file to Tableau Cloud/Server.

    This script handles the publication of a .hyper datasource into a specific
    Tableau project with configurable publish mode.

    Args:
        cfg: Configuration wrapper containing environment settings.
        args: Command-line arguments containing script name.

    Publishing Modes:
        - CreateNew: Create a new datasource
        - Append: Append data to an existing datasource
        - Overwrite: Replace the existing datasource
    """
    # Log the start of the script execution
    logger.info(f"Starting script: {args.script}")

    # ---------------------------------------------------------------------
    # Configuration: Update these values for your use case
    # ---------------------------------------------------------------------
    # Path to the Hyper file to publish
    hyper_filepath = "$REPLACE_WITH_YOUR_HYPER_PATH"

    # Target Tableau project LUID where the datasource will be published
    project_luid = "$REPLACE_WITH_YOUR_PROJECT_LUID"

    # Publishing mode: CreateNew, Append, or Overwrite
    mode = "CreateNew"

    # ---------------------------------------------------------------------
    # Publish the datasource to Tableau
    # ---------------------------------------------------------------------
    with log_duration(args.script):
        with TableauClient() as tsc:
            tsc.publish_datasources(
                server=tsc.server,
                filepath=hyper_filepath,
                project_luid=project_luid,
                mode=mode,
            )

    logger.info(f"Script finished: {args.script}")
