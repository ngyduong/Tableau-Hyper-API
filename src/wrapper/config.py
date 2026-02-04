from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclass(frozen=True)
class TabCredentials:
    pat_name: str
    pat_secret: str
    site_id: str
    site_url: str
    api_version: Optional[str] = None


@dataclass(frozen=True)
class DatabricksCredentials:
    databricks_server_hostname: str
    databricks_http_path: str
    databricks_token: str


class ConfigWrapper(metaclass=Singleton):
    """
    Centralised config access.
    Loaded once, reused everywhere.
    """

    def __init__(self) -> None:
        self._tab_cred = TabCredentials(
            pat_name=os.getenv("tab_pat_name", ""),
            pat_secret=os.getenv("tab_secret_id", ""),
            site_id=os.getenv("tab_site_id", ""),
            site_url=os.getenv("tab_site_url", ""),
            api_version=os.getenv("tab_api_version", ""),
        )
        self._databricks_cred = DatabricksCredentials(
            databricks_server_hostname=os.getenv("databricks_server_hostname", ""),
            databricks_http_path=os.getenv("databricks_http_path", ""),
            databricks_token=os.getenv("databricks_token", ""),
        )

    @property
    def tab_cred(self) -> TabCredentials:
        self._validate_tableau()
        return self._tab_cred

    def _validate_tableau(self) -> None:
        missing = [
            name
            for name, value in vars(self._tab_cred).items()
            if name != "api_version" and not value
        ]
        if missing:
            raise ValueError(f"Missing Tableau config vars: {missing}")

    @property
    def databricks_cred(self) -> DatabricksCredentials:
        self._validate_databricks()
        return self._databricks_cred

    def _validate_databricks(self) -> None:
        missing = [
            name for name, value in vars(self._databricks_cred).items() if not value
        ]
        if missing:
            raise ValueError(f"Missing Databricks config vars: {missing}")
