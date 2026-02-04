"""Main CLI Entrypoint.

This module serves as the main entry point for the Tableau project.
It routes commands to the appropriate scripts based on user input.
"""

from __future__ import annotations

import argparse
import logging
from typing import Callable, Dict

from src.scripts.hyper_api.generate_hyper_from_csv import (
    main as main_generate_hyper_from_csv,
)
from src.scripts.hyper_api.generate_hyper_with_databricks import (
    main as main_generate_hyper_with_databricks,
)
from src.scripts.hyper_api.publish_hyper import main as main_publish_hyper
from src.utils.logging_setup import setup_logging
from src.wrapper.config import ConfigWrapper

ScriptFn = Callable[[ConfigWrapper, argparse.Namespace], None]
logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build and configure the argument parser.

    Returns:
        Configured ArgumentParser with script selection options.
    """
    parser = argparse.ArgumentParser(description="Project entrypoint")
    parser.add_argument(
        "--script",
        required=True,
        choices=[
            "generate_hyper_from_csv",
            "generate_hyper_with_databricks",
            "publish_hyper",
        ],
        help="Which script to run",
    )

    return parser


def main() -> int:
    """Main entry point for the CLI application.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    # Initialize logging system
    setup_logging(app_name="tableau-cli")
    logger.info("Starting CLI")

    # Parse command-line arguments
    parser = build_parser()
    args = parser.parse_args()

    # Load and validate configuration (raises ValueError if missing env vars)
    cfg = ConfigWrapper()

    scripts: Dict[str, ScriptFn] = {
        "generate_hyper_from_csv": main_generate_hyper_from_csv,
        "generate_hyper_with_databricks": main_generate_hyper_with_databricks,
        "publish_hyper": main_publish_hyper,
    }

    script_fn = scripts.get(args.script)
    script_fn(cfg, args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
