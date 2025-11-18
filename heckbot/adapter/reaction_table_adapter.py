from __future__ import annotations

import os
from typing import Mapping
from typing import Sequence

from pynamodb.attributes import ListAttribute
from pynamodb.attributes import UnicodeAttribute
from pynamodb.exceptions import DeleteError
from pynamodb.exceptions import DoesNotExist
from pynamodb.exceptions import GetError
from pynamodb.models import Model


class ReactionAssociation(Model):
    class Meta:
        read_capacity_units = 1
        write_capacity_units = 1
        table_name = 'HeckBotReactions'
        host = os.environ['AWS_HOST']
    guild_id: UnicodeAttribute = UnicodeAttribute(hash_key=True)
    pattern: UnicodeAttribute = UnicodeAttribute(range_key=True)
    reactions: ListAttribute[str] = ListAttribute(default=list)


class ReactionTableAdapter:

    def __init__(self):
        if not ReactionAssociation.exists():
            ReactionAssociation.create_table()

    @classmethod
    def get_all_reactions(
            cls,
            guild_id: str,
    ) -> Mapping[str, Sequence[str]]:
        """
        Finds all reactions for a given guild
        :param guild_id: Guild ID to match (PK)
        :return: a mapping of patterns to sequences of reactions
        """
        return {q.pattern: q.reactions for q in ReactionAssociation.query(guild_id)}

    @classmethod
    def get_reactions(
            cls,
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
        reactions: list[str] = ReactionAssociation.get(guild_id, pattern).reactions
        return reactions

    @classmethod
    def add_reaction(
            cls,
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
        try:
            association = ReactionAssociation.get(guild_id, pattern)
            association.reactions.append(reaction)
        except GetError:
            association = ReactionAssociation(
                guild_id, pattern, reactions=[reaction],
            )
        except DoesNotExist:
            association = ReactionAssociation(
                guild_id, pattern, reactions=[reaction],
            )
        association.save()

    @classmethod
    def remove_all_reactions(
            cls,
            guild_id: str,
            pattern: str,
    ) -> None:
        """
        Removes all reactions to a given pattern in a given guild in the
        ReactionTableAdapter.
        :param guild_id: Guild ID to match (PK)
        :param pattern: pattern to match (SK)
        """
        try:
            association = ReactionAssociation.get(guild_id, pattern)
            association.delete()
        except GetError:
            return  # TODO more
        except DoesNotExist:
            return  # TODO more
        except DeleteError:
            return  # TODO more

    @classmethod
    def remove_reaction(
            cls,
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
        try:
            association = ReactionAssociation.get(guild_id, pattern)
            association.reactions.remove(reaction)
            association.save()
        except GetError:
            return  # TODO more
        except DoesNotExist:
            return  # TODO more
        except DeleteError:
            return  # TODO more
