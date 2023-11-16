from __future__ import annotations

import sqlite3
import threading
from typing import Any
from typing import Optional


class SqliteAdaptor:
    def __init__(
            self,
    ) -> None:
        """
        Constructor method
        """
        self._connection = None
        self._lock = threading.Lock()

    @property
    def cursor(self):
        if self._connection is None:
            self._connection = sqlite3.connect('roles.db')
            self._connection.row_factory = sqlite3.Row
        return self._connection.cursor()

    def commit_and_close(self):
        # with self._lock:
        if self._connection:
            self._connection.commit()
            self._connection.close()
            self._connection = None

    def run_query(
            self, query: str,
            params: tuple | None = None,
    ) -> list[dict[str, Any]]:
        try:
            if params is None:
                params = {}
            with self._lock:
                return self.cursor.execute(query, params).fetchall()
        except sqlite3.Error as ex:
            print(
                f'Got exception {ex} when running query '
                f'{query} with params {params}',
            )

    def run_query_many(
            self, query: str,
            params_list: list[tuple] | None = None,
    ) -> list[dict[str, Any]]:
        try:
            if params_list is None:
                params_list = {}
            with self._lock:
                return self.cursor.executemany(query, params_list).fetchall()
        except sqlite3.Error as ex:
            print(
                f'Got exception {ex} when running query many '
                f'{query} with params list {params_list}',
            )
