from __future__ import annotations

import argparse
import logging

from src.utils.log_duration import log_duration
from src.wrapper.config import ConfigWrapper
from src.wrapper.tableau_wrapper import TableauClient

logger = logging.getLogger(__name__)


def main(cfg: ConfigWrapper, args: argparse.Namespace) -> None:
    """
    Publish a Hyper file to Tableau Cloud / Tableau Server.

    This script handles the publication of a .hyper datasource
    into a specific Tableau project, with a configurable publish mode.
    """

    # Log the start of the script execution
    logger.info("Starting script: publish_hyper")

    # Path to the Hyper file to publish (to be replaced at runtime or via config)
    hyper_filepath = "$REPLACE_WITH_YOUR_HYPER_PATH"

    # Target Tableau project LUID where the datasource will be published
    project_luid = "$REPLACE_WITH_YOUR_PROJECT_LUID"

    # Publishing mode:
    # - CreateNew: create a new datasource
    # - Append: append data to an existing datasource
    # - Overwrite: replace the existing datasource
    mode = "CreateNew"

    # Measure and log the duration of the publish step
    with log_duration("publish_hyper"):
        with TableauClient() as tsc:
            tsc.publish_datasources(
                server=tsc.server,
                filepath=hyper_filepath,
                project_luid=project_luid,
                mode=mode,
            )

    # Log the successful end of the script
    logger.info("Script finished: publish_hyper")
