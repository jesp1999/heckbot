from __future__ import annotations

import os
from typing import Sequence

from pynamodb.attributes import ListAttribute
from pynamodb.attributes import UnicodeAttribute
from pynamodb.exceptions import DeleteError
from pynamodb.exceptions import DoesNotExist
from pynamodb.exceptions import GetError
from pynamodb.models import Model


class MessageAssociation(Model):
    class Meta:
        read_capacity_units = 1
        write_capacity_units = 1
        table_name = 'HeckBotMessageReactions'
        host = os.environ['AWS_HOST']

    guild_id: UnicodeAttribute = UnicodeAttribute(hash_key=True)
    pattern: UnicodeAttribute = UnicodeAttribute(range_key=True)
    messages: ListAttribute[str] = ListAttribute(default=list)


class MessageTableAdapter:

    def __init__(self):
        if not MessageAssociation.exists():
            MessageAssociation.create_table()

    @classmethod
    def get_all_messages(
            cls,
            guild_id: str,
    ) -> dict[str, Sequence[str]]:
        """
        Finds all messages for a given guild
        :param guild_id: Guild ID to match (PK)
        :return: a list of messages
        """
        return {q.pattern: q.messages for q in MessageAssociation.query(guild_id)}

    @classmethod
    def get_messages(
            cls,
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
        messages: list[str] = MessageAssociation.get(guild_id, pattern).messages
        return messages

    @classmethod
    def add_message(
            cls,
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
        try:
            association = MessageAssociation.get(guild_id, pattern)
            association.messages.append(message)
        except GetError:
            association = MessageAssociation(
                guild_id, pattern, messages=[message],
            )
        except DoesNotExist:
            association = MessageAssociation(
                guild_id, pattern, messages=[message],
            )
        association.save()

    @classmethod
    def remove_all_messages(
            cls,
            guild_id: str,
            pattern: str,
    ) -> None:
        """
        Removes all message responses to a given pattern in a given
         guild in the MessageTableAdapter
        :param guild_id: Guild ID to match (PK)
        :param pattern: pattern to match (SK)
        """
        try:
            association = MessageAssociation.get(guild_id, pattern)
            association.delete()
        except GetError:
            return  # TODO more
        except DoesNotExist:
            return  # TODO more
        except DeleteError:
            return  # TODO more

    @classmethod
    def remove_message(
            cls,
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
        try:
            association = MessageAssociation.get(guild_id, pattern)
            association.messages.remove(message)
            association.save()
        except GetError:
            return  # TODO more
        except DoesNotExist:
            return  # TODO more
        except DeleteError:
            return  # TODO more
