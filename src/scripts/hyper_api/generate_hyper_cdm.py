from __future__ import annotations

import argparse
import logging
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
from src.wrapper.tableau_wrapper import TableauClient

logger = logging.getLogger(__name__)


def main(tsc: TableauClient, cfg: ConfigWrapper, args: argparse.Namespace) -> None:
    """
    Generate a Tableau Hyper file

    Workflow:
    1. Read a source file (CSV in this example)
    2. Export it to parquet (intermediate format)
    3. Create or reuse a Hyper file
    4. Create the schema/table if needed
    5. Insert parquet data into the Hyper table
    """

    logger.info("Starting script: generate_hyper")

    with log_duration("generate_hyper"):

        # ---------------------------------------------------------------------
        # Create temporary directories used to store parquet files and the hyper file
        # These folders are created if they do not already exist
        # ---------------------------------------------------------------------
        # parquet_dir = Path("temp/pokemon/generate_hyper/parquet_files")
        # parquet_dir.mkdir(parents=True, exist_ok=True)
        #
        # hyper_path = Path("temp/pokemon/generate_hyper/hyper_file/pokemon.hyper")
        # hyper_path.parent.mkdir(parents=True, exist_ok=True)

        # ---------------------------------------------------------------------
        # Read the source data into a pandas DataFrame
        # In this example we read a CSV, but any format supported by pandas
        # (JSON, Excel, etc.) could be used here
        # ---------------------------------------------------------------------
        # df = pd.read_csv("sample_data/pokemon.csv", encoding="utf-8")

        # Export the DataFrame to parquet.
        # Parquet is used as an intermediate format because it is columnar,
        # fast to read, and natively supported by the Hyper `external()` function.
        # parquet_path = parquet_dir / "pokemon.parquet"
        # df.to_parquet(parquet_path, index=False)

        # ---------------------------------------------------------------------
        # Collect all parquet files that should be loaded into the Hyper file
        # Files are sorted to ensure deterministic loading order
        # ---------------------------------------------------------------------
        parquet_dir = Path(
            "/Users/mac-DNGUYE52/PycharmProjects/des-tableau-python/parquet_files"
        )
        hyper_path = Path(
            "/Users/mac-DNGUYE52/PycharmProjects/des-tableau-python/obt_sales_metrics__gmv_ordered_receipts.hyper"
        )

        parquet_files = sorted(parquet_dir.glob("*.parquet"))

        # ---------------------------------------------------------------------
        # Start the Hyper process and open a connection to the Hyper file
        # CREATE_IF_NOT_EXISTS ensures we reuse the file if it already exists
        # ---------------------------------------------------------------------
        with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            with Connection(
                endpoint=hyper.endpoint,
                database=str(hyper_path),
                create_mode=CreateMode.CREATE_IF_NOT_EXISTS,
            ) as connection:

                # -----------------------------------------------------------------
                # Define the schema and table name.
                # Tableau extracts conventionally use Extract.Extract
                # -----------------------------------------------------------------
                schema_name = "Extract"
                table_name = "Extract"
                schema_table = f'"{schema_name}"."{table_name}"'

                # Ensure the schema exists (idempotent operation)
                connection.execute_command(
                    f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'
                )

                # -----------------------------------------------------------------
                # Load parquet data into the Hyper file
                #
                # - If the table already exists: append data (INSERT)
                # - If the table does not exist yet: create it from the first parquet
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
                        logger.info(
                            "Parquet file appended successfully: %s", parquet_name
                        )

                    except Exception:
                        connection.execute_command(
                            f"CREATE TABLE {schema_table} AS "
                            f"(SELECT * FROM external({p_sql}, FORMAT => 'parquet'))"
                        )
                        logger.info(
                            "Parquet file used to create Hyper table: %s", parquet_name
                        )

    logger.info("Script finished: generate_hyper")
