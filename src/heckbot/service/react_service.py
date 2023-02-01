from __future__ import annotations

from typing import Optional

from heckbot.adaptor.dynamo_table_adaptor import DynamoTableAdaptor


class AssociationService:
    """
    Service class which encapsulates all logic behind association
    commands from the react-match cog.
    """
    _association_table: DynamoTableAdaptor = DynamoTableAdaptor(
        table_name='HeckBotAssociations',
        pk_name='Server',
        sk_name='Pattern',
    )

    def get_all_associations(
            self,
            guild: str,
    ) -> dict[str, list[str]]:
        """
        Gets all text-pattern-to-emoji mappings for a given guild.
        :param guild: Identifier for the guild
        :return: Mapping of text patterns to lists of associated emojis
        in order
        """
        results = self._association_table.read(
            pk_value=guild,
        )
        if results is None:
            return {}

        associations = {
            result['Pattern']: result['Reactions']
            for result in results
        }
        return associations

    def get_associations_for_pattern(
            self,
            guild: str,
            pattern: str,
    ) -> list[str]:
        """
        Gets all emojis associated with a given guild and text-pattern
        for a given guild.
        :param guild: Identifier for the guild
        :param pattern: Text pattern
        :return: List of associated emojis in order
        """
        associations = self._association_table.read(
            pk_value=guild,
            sk_value=pattern,
        )
        if associations is None:
            return []
        return associations[0].get('Reactions')

    def add_association(
            self,
            guild: str,
            pattern: str,
            reaction: str,
    ) -> None:
        """
        Adds a text-pattern-to-emoji association for a given guild.
        :param guild: Identifier for the guild
        :param pattern: Text pattern
        :param reaction: Emoji to be reacted
        """
        self._association_table.add_list_item(
            pk_value=guild,
            sk_value=pattern,
            list_key_name='Reactions',
            list_item=reaction,
        )

    def remove_association(
            self,
            guild: str,
            pattern: str,
            reaction: str | None = None,
    ) -> None:
        """
        Removes all emoji associations to a given text-pattern for a
        given guild.
        :param guild: Identifier for the guild
        :param pattern: Text pattern
        :param reaction: Emoji to be reacted
        """
        if reaction is None:
            self._association_table.delete(
                pk_value=guild,
                sk_value=pattern,
            )
        else:
            self._association_table.remove_list_item(
                pk_value=guild,
                sk_value=pattern,
                list_key_name='Reactions',
                list_item=reaction,
            )
