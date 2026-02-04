from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path

import pandas as pd
from tableauhyperapi import (
    Connection,
    CreateMode,
    HyperProcess,
    Telemetry,
    escape_string_literal,
)

from src.utils.log_duration import log_duration
from src.wrapper.config import ConfigWrapper

logger = logging.getLogger(__name__)


def main(cfg: ConfigWrapper, args: argparse.Namespace) -> None:
    """
    Generate a Tableau Hyper file from CSV data.

    Workflow:
        1. Read source data from a CSV file
        2. Export data to Parquet format (intermediate format)
        3. Create or reuse a Hyper file
        4. Create the schema/table if needed
        5. Insert Parquet data into the Hyper table

    Args:
        cfg: Configuration wrapper containing environment settings.
        args: Command-line arguments containing script name.
    """

    logger.info(f"Starting script: {args.script}")

    with log_duration(args.script):

        # ---------------------------------------------------------------------
        # Source file configuration
        # Define the CSV file to be processed. Any pandas-readable format
        # (CSV, JSON, Excel, etc.) can be used with an absolute or relative path.
        # ---------------------------------------------------------------------
        csv_filepath = "sample_data/pokemon.csv"
        csv_filename = re.search(r"(?<=/)[^/]+(?=\.csv$)", csv_filepath).group()

        # ---------------------------------------------------------------------
        # Create temporary directories for Parquet files and Hyper file
        # Directories are created if they do not already exist
        # ---------------------------------------------------------------------
        parquet_dir = Path(f"temp/{csv_filename}/{args.script}/parquet_files")
        parquet_dir.mkdir(parents=True, exist_ok=True)

        hyper_path = Path(
            f"temp/{csv_filename}/{args.script}/hyper_file/{csv_filename}.hyper"
        )
        hyper_path.parent.mkdir(parents=True, exist_ok=True)

        # ---------------------------------------------------------------------
        # Read source data into a pandas DataFrame
        # Any pandas-supported format (CSV, JSON, Excel, etc.) can be used
        # ---------------------------------------------------------------------
        df = pd.read_csv(csv_filepath, encoding="utf-8")

        # ---------------------------------------------------------------------
        # Export DataFrame to Parquet format
        # Parquet is used as intermediate format because it is columnar,
        # fast to read, and natively supported by Hyper's external() function
        # ---------------------------------------------------------------------
        parquet_path = parquet_dir / f"{csv_filename}.parquet"
        df.to_parquet(parquet_path, index=False)

        # ---------------------------------------------------------------------
        # Collect all Parquet files to be loaded into the Hyper file
        # Files are sorted to ensure deterministic loading order
        # ---------------------------------------------------------------------
        parquet_files = sorted(parquet_dir.glob("*.parquet"))

        # ---------------------------------------------------------------------
        # Start Hyper process and open connection to the Hyper file
        # CREATE_IF_NOT_EXISTS mode reuses the file if it already exists
        # ---------------------------------------------------------------------
        with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            with Connection(
                endpoint=hyper.endpoint,
                database=str(hyper_path),
                create_mode=CreateMode.CREATE_IF_NOT_EXISTS,
            ) as connection:

                # -----------------------------------------------------------------
                # Define schema and table name
                # Tableau extracts conventionally use Extract.Extract as default
                # -----------------------------------------------------------------
                schema_name = "Extract"
                table_name = "Extract"
                schema_table = f'"{schema_name}"."{table_name}"'

                # Ensure schema exists (idempotent operation)
                connection.execute_command(
                    f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'
                )

                # -----------------------------------------------------------------
                # Load Parquet data into the Hyper file
                # - If table exists: Append data (INSERT)
                # - If table does not exist: Create it from the first Parquet file
                # -----------------------------------------------------------------
                for p in parquet_files:

                    parquet_name = p.name
                    logger.info("Starting parquet ingestion: %s", parquet_name)
                    p_sql = escape_string_literal(str(p.resolve()))

                    try:
                        connection.execute_command(
                            f"INSERT INTO {schema_table} "
                            f"(SELECT * FROM external({p_sql}, FORMAT => 'parquet'))"
                        )

                    except Exception:
                        connection.execute_command(
                            f"CREATE TABLE {schema_table} AS "
                            f"(SELECT * FROM external({p_sql}, FORMAT => 'parquet'))"
                        )
                        logger.info(
                            "Parquet file used to create Hyper table: %s", parquet_name
                        )

    logger.info(f"Script finished: {args.script}")
