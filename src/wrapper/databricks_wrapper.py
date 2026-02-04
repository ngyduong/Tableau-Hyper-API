from __future__ import annotations

from databricks import sql

from src.wrapper.config import ConfigWrapper


class DatabricksClient:
    """
    Thin, safe wrapper around databricks-sql-connector.
    Uses ConfigWrapper for credentials.
    """

    def __init__(self) -> None:
        cfg = ConfigWrapper().databricks_cred

        self.connection = sql.connect(
            server_hostname=cfg.databricks_server_hostname,
            http_path=cfg.databricks_http_path,
            access_token=cfg.databricks_token,
        )

    def execute_query(self, query: str):
        """Execute a SQL query and return a pandas DataFrame using Arrow format.

        This method uses fetchall_arrow().to_pandas() which:
        - Preserves proper data types from Databricks
        - Is more efficient for large datasets
        - Handles type conversion automatically

        Args:
            query: SQL query to execute

        Returns:
            pandas DataFrame with proper data types
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            # Use Arrow format for better type preservation and performance
            return cursor.fetchall_arrow().to_pandas()

    def close(self) -> None:
        """Close the Databricks connection."""
        if self.connection:
            self.connection.close()
