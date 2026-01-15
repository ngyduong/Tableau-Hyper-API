from __future__ import annotations

import argparse
import logging

import pandas as pd

from src.utils.log_duration import log_duration
from src.wrapper.config import ConfigWrapper
from src.wrapper.tableau_wrapper import TableauClient

logger = logging.getLogger(__name__)


def main(tsc: TableauClient, cfg: ConfigWrapper, args: argparse.Namespace) -> None:
    logger.info("Starting script: generate_hyper")

    with log_duration("generate_hyper"):

        df = pd.read_csv(
            "sample_data/pokemon.csv",
            sep=",",
            encoding="utf-8",
            header=0,  # row with column names
        )

        print(df.head())

    logger.info("Script finished: generate_hyper")
