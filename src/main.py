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

from src.scripts.hyper_api.generate_hyper import main as main_generate_hyper
from src.scripts.hyper_api.publish_hyper import main as main_publish_hyper
from src.utils.logging_setup import setup_logging
from src.wrapper.config import ConfigWrapper

ScriptFn = Callable[[ConfigWrapper, argparse.Namespace], None]
logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project entrypoint")
    parser.add_argument(
        "--script",
        required=True,
        choices=["generate_hyper", "publish_hyper"],
        help="Which script to run",
    )

    return parser


def main() -> int:
    setup_logging(app_name="tableau-cli")
    logger.info("Starting CLI")
    parser = build_parser()
    args = parser.parse_args()

    # Load & validate config once (raises ValueError if missing env vars)
    cfg = ConfigWrapper()

    scripts: Dict[str, ScriptFn] = {
        "generate_hyper": main_generate_hyper,
        "publish_hyper": main_publish_hyper,
    }

    script_fn = scripts.get(args.script)
    if not script_fn:
        print(f"No script found: {args.script}", file=sys.stderr)
        return 2

    script_fn(cfg, args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
