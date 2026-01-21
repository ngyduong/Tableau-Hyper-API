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
    logger.info("Starting script: generate_hyper")

    with log_duration("generate_hyper"):
        parquet_dir = Path("temp/pokemon/generate_hyper/parquet_files")
        parquet_dir.mkdir(parents=True, exist_ok=True)

        tmp_parquet_file = parquet_dir / "pokemon.parquet"

        hyper_dir = Path("temp/pokemon/generate_hyper/hyper_file")
        hyper_dir.mkdir(parents=True, exist_ok=True)
        tmp_hyper_file = hyper_dir / "pokemon.hyper"

        with log_duration("read_csv"):
            df = pd.read_csv(
                "sample_data/pokemon.csv", sep=",", encoding="utf-8", header=0
            )

        with log_duration("write_parquet"):
            df.to_parquet(tmp_parquet_file, index=False)

        schema_name = "Extract"
        table_name = "Extract"
        schema_table = f'"{schema_name}"."{table_name}"'

        parquet_files = sorted(
            [p for p in parquet_dir.iterdir() if p.is_file() and p.suffix == ".parquet"]
        )
        if not parquet_files:
            raise RuntimeError(f"No parquet files found in {parquet_dir}")

        with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            with Connection(
                endpoint=hyper.endpoint,
                database=str(tmp_hyper_file),
                create_mode=CreateMode.CREATE_IF_NOT_EXISTS,
            ) as connection:

                # ✅ Idempotent schema creation
                connection.execute_command(
                    f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'
                )

                # ✅ Check whether the table already exists in the hyper file
                existing_tables = {
                    t.name.unescaped
                    for t in connection.catalog.get_table_names(schema_name)
                }
                table_exists = table_name in existing_tables

                for i, parquet_file in enumerate(parquet_files):
                    parquet_sql_path = escape_string_literal(
                        str(parquet_file.resolve())
                    )

                    if (not table_exists) and i == 0:
                        # Create table from the first parquet
                        query = (
                            f"CREATE TABLE {schema_table} AS "
                            f"(SELECT * FROM external({parquet_sql_path}, FORMAT => 'parquet'))"
                        )
                        table_exists = True
                    else:
                        # Append rows
                        query = (
                            f"INSERT INTO {schema_table} "
                            f"(SELECT * FROM external({parquet_sql_path}, FORMAT => 'parquet'))"
                        )

                    connection.execute_command(query)

    logger.info("Script finished: generate_hyper")
