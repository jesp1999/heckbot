from __future__ import annotations

from collections import defaultdict
from typing import Sequence

from heckbot.adapter.sqlite_adaptor import SqliteAdaptor


class MessageTableAdapter:

    def __init__(self) -> None:
        self._db = SqliteAdaptor()
        self._db.run_query('''\
            CREATE TABLE IF NOT EXISTS message_associations
            (guild_id TEXT NOT NULL,
            pattern TEXT NOT NULL,
            message TEXT NOT NULL,
            PRIMARY KEY (guild_id, pattern, message));
        ''')
        self._db.commit_and_close()

    def get_all_messages(
            self,
            guild_id: str,
    ) -> dict[str, Sequence[str]]:
        """
        Finds all messages for a given guild
        :param guild_id: Guild ID to match (PK)
        :return: a list of messages
        """
        rows = self._db.run_query(
            '''SELECT pattern, message FROM message_associations
            WHERE guild_id=?;''',
            (guild_id,),
        )
        associations: dict[str, list[str]] = defaultdict(list)
        for row in rows:
            associations[row['pattern']].append(row['message'])
        self._db.commit_and_close()
        return dict(associations)

    def get_messages(
            self,
            guild_id: str,
            pattern: str | None = None,
    ) -> Sequence[str]:
        """
        Finds the desired messages for a given guild and (optionally)
         pattern in the MessageTableAdapter
        :param guild_id: Guild ID to match (PK)
        :param pattern: pattern to match (SK)
        :return: a list of messages
        """
        rows = self._db.run_query(
            '''SELECT message FROM message_associations
            WHERE guild_id=? AND pattern=?;''',
            (guild_id, pattern),
        )
        self._db.commit_and_close()
        return [row['message'] for row in rows]

    def add_message(
            self,
            guild_id: str,
            pattern: str,
            message: str,
    ) -> None:
        """
        Adds the given message to the given guild id and pattern in the
         MessageTableAdapter
        :param guild_id: Guild ID to match (PK)
        :param pattern: pattern to match (SK)
        :param message: Message to add
        """
        self._db.run_query(
            '''INSERT OR IGNORE INTO message_associations
            (guild_id, pattern, message) VALUES (?, ?, ?);''',
            (guild_id, pattern, message),
        )
        self._db.commit_and_close()

    def remove_all_messages(
            self,
            guild_id: str,
            pattern: str,
    ) -> None:
        """
        Removes all message responses to a given pattern in a given
         guild in the MessageTableAdapter
        :param guild_id: Guild ID to match (PK)
        :param pattern: pattern to match (SK)
        """
        self._db.run_query(
            '''DELETE FROM message_associations
            WHERE guild_id=? AND pattern=?;''',
            (guild_id, pattern),
        )
        self._db.commit_and_close()

    def remove_message(
            self,
            guild_id: str,
            pattern: str,
            message: str,
    ) -> None:
        """
        Removes the specified association
        :param guild_id: Guild ID to match (PK)
        :param pattern: pattern to match (SK)
        :param message: Message to remove (if unspecified, will remove
        all)
        """
        self._db.run_query(
            '''DELETE FROM message_associations
            WHERE guild_id=? AND pattern=? AND message=?;''',
            (guild_id, pattern, message),
        )
        self._db.commit_and_close()
