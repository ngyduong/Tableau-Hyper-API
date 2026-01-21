from __future__ import annotations

import time
from typing import Any, Callable, List

import tableauserverclient as TSC

from src.wrapper.config import ConfigWrapper


class TableauClient:
    """
    Thin, safe wrapper around tableau-server-client.
    Uses ConfigWrapper for credentials.
    """

    def __init__(self) -> None:
        cfg = ConfigWrapper().tab_cred

        self._server = TSC.Server(
            cfg.site_url,
            use_server_version=cfg.api_version is None,
        )
        if cfg.api_version:
            self._server.version = cfg.api_version

        self._auth = TSC.PersonalAccessTokenAuth(
            token_name=cfg.pat_name,
            personal_access_token=cfg.pat_secret,
            site_id=cfg.site_id,
        )
        self._signed_in = False

    # ---------- Auth lifecycle ----------

    def sign_in(self) -> None:
        if not self._signed_in:
            self._server.auth.sign_in(self._auth)
            self._signed_in = True

    def sign_out(self) -> None:
        if self._signed_in:
            self._server.auth.sign_out()
            self._signed_in = False

    def __enter__(self) -> "TableauClient":
        self.sign_in()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.sign_out()

    @property
    def server(self) -> TSC.Server:
        return self._server

    # ---------- Pagination helper ----------

    def list_all(self, getter: Callable[[TSC.RequestOptions], Any]) -> List[Any]:
        items: List[Any] = []
        page = 1

        while True:
            ro = TSC.RequestOptions()
            ro.paging.page_number = page
            ro.paging.page_size = 1000

            chunk, pagination = getter(ro)
            items.extend(chunk)

            if pagination.total_available <= len(items):
                break

            page += 1

        return items

    # ---------- Common helpers ----------

    def publish_datasources(self, server, filepath, project_luid, mode):
        new_datasource = TSC.DatasourceItem(project_luid)
        server.datasources.publish(new_datasource, file=filepath, mode=mode)
