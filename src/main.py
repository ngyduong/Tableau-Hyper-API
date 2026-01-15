"""
Main
====================================
The core module of the project
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Callable, Dict

from src.scripts.hyper_api_create_extract import \
    main as run_hyper_api_create_extract
from src.utils.logging_setup import setup_logging
from src.wrapper.config import ConfigWrapper
from src.wrapper.tableau_wrapper import TableauClient

ScriptFn = Callable[[TableauClient, ConfigWrapper, argparse.Namespace], None]
logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project entrypoint")
    parser.add_argument(
        "--script",
        required=True,
        choices=[
            "hyper_api_create_extract",
        ],
        help="Which script to run",
    )

    return parser


def main() -> int:
    setup_logging(app_name="tableau-cli")  # reads LOG_LEVEL env by default
    logger.info("Starting CLI")
    parser = build_parser()
    args = parser.parse_args()

    # Load & validate config once (raises ValueError if missing env vars)
    cfg = ConfigWrapper()

    scripts: Dict[str, ScriptFn] = {
        "hyper_api_create_extract": run_hyper_api_create_extract,
    }

    script_fn = scripts.get(args.script)
    if not script_fn:
        print(f"No script found: {args.script}", file=sys.stderr)
        return 2

    # One shared Tableau session for the whole run
    with TableauClient() as tc:
        script_fn(tc, cfg, args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
