from __future__ import annotations

from collections import defaultdict
from typing import Mapping
from typing import Sequence

from heckbot.adapter.sqlite_adaptor import SqliteAdaptor


class ReactionTableAdapter:

    def __init__(self) -> None:
        self._db = SqliteAdaptor()
        self._db.run_query('''\
            CREATE TABLE IF NOT EXISTS reaction_associations
            (guild_id TEXT NOT NULL,
            pattern TEXT NOT NULL,
            reaction TEXT NOT NULL,
            PRIMARY KEY (guild_id, pattern, reaction));
        ''')
        self._db.commit_and_close()

    def get_all_reactions(
            self,
            guild_id: str,
    ) -> Mapping[str, Sequence[str]]:
        """
        Finds all reactions for a given guild
        :param guild_id: Guild ID to match (PK)
        :return: a mapping of patterns to sequences of reactions
        """
        rows = self._db.run_query(
            '''SELECT pattern, reaction FROM reaction_associations
            WHERE guild_id=?;''',
            (guild_id,),
        )
        associations: dict[str, list[str]] = defaultdict(list)
        for row in rows:
            associations[row['pattern']].append(row['reaction'])
        self._db.commit_and_close()
        return dict(associations)

    def get_reactions(
            self,
            guild_id: str,
            pattern: str | None = None,
    ) -> Sequence[str]:
        """
        Finds the desired reactions for a given guild and (optionally)
        pattern in the ReactionTableAdapter
        :param guild_id: Guild ID to match (PK)
        :param pattern: pattern to match (SK)
        :return: a sequence of reactions
        """
        rows = self._db.run_query(
            '''SELECT reaction FROM reaction_associations
            WHERE guild_id=? AND pattern=?;''',
            (guild_id, pattern),
        )
        self._db.commit_and_close()
        return [row['reaction'] for row in rows]

    def add_reaction(
            self,
            guild_id: str,
            pattern: str,
            reaction: str,
    ) -> None:
        """
        Adds the given reaction to the given guild id and pattern in the
        ReactionTableAdapter.
        :param guild_id: Guild ID to match (PK)
        :param pattern: pattern to match (SK)
        :param reaction: Reaction to add
        """
        self._db.run_query(
            '''INSERT OR IGNORE INTO reaction_associations
            (guild_id, pattern, reaction) VALUES (?, ?, ?);''',
            (guild_id, pattern, reaction),
        )
        self._db.commit_and_close()

    def remove_all_reactions(
            self,
            guild_id: str,
            pattern: str,
    ) -> None:
        """
        Removes all reactions to a given pattern in a given guild in the
        ReactionTableAdapter.
        :param guild_id: Guild ID to match (PK)
        :param pattern: pattern to match (SK)
        """
        self._db.run_query(
            '''DELETE FROM reaction_associations
            WHERE guild_id=? AND pattern=?;''',
            (guild_id, pattern),
        )
        self._db.commit_and_close()

    def remove_reaction(
            self,
            guild_id: str,
            pattern: str,
            reaction: str,
    ) -> None:
        """
        Removes the given reaction from the given guild id and pattern
        in the ReactionTableAdapter.
        :param guild_id: Guild ID to match (PK)
        :param pattern: pattern to match (SK)
        :param reaction: Reaction to remove
        """
        self._db.run_query(
            '''DELETE FROM reaction_associations
            WHERE guild_id=? AND pattern=? AND reaction=?;''',
            (guild_id, pattern, reaction),
        )
        self._db.commit_and_close()
