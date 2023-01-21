from src.adaptor.dynamo_table_adaptor import DynamoTableAdaptor


class AssociationService:
    """
    Service class which encapsulates all logic behind association
    commands from the react-match cog.
    """
    _association_table: DynamoTableAdaptor = DynamoTableAdaptor(
        table_name='HeckBotAssociations',
        pk_name='Server',
        sk_name='Pattern'
    )

    def get_all_associations(
            self,
            server: str
    ) -> dict[str, list[str]]:
        """
        Gets all text-pattern-to-emoji mappings for a given server.
        :param server: Identifier for the server
        :return: Mapping of text patterns to lists of associated emojis
        in order
        """
        results = self._association_table.read(
            pk_value=server
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
            server: str,
            pattern: str
    ) -> list[str]:
        """
        Gets all emojis associated with a given server and text-pattern
        for a given server.
        :param server: Identifier for the server
        :param pattern: Text pattern
        :return: List of associated emojis in order
        """
        return self._association_table.read(
            pk_value=server,
            sk_value=pattern
        )[0].get('Reactions')

    def add_association(
            self,
            server: str,
            pattern: str,
            reaction: str
    ) -> None:
        """
        Adds a text-pattern-to-emoji association for a given server.
        :param server: Identifier for the server
        :param pattern: Text pattern
        :param reaction: Emoji to be reacted
        """
        self._association_table.add_list_item(
            pk_value=server,
            sk_value=pattern,
            list_key_name='Reactions',
            list_item=reaction
        )

    def remove_association(
            self,
            server: str,
            pattern: str,
            reaction: str = None
    ) -> None:
        """
        Removes all emoji associations to a given text-pattern for a
        given server.
        :param server: Identifier for the server
        :param pattern: Text pattern
        :param reaction: Emoji to be reacted
        """
        if reaction is None:
            self._association_table.delete(
                pk_value=server,
                sk_value=pattern
            )
        else:
            self._association_table.remove_list_item(
                pk_value=server,
                sk_value=pattern,
                list_key_name='Reactions',
                list_item=reaction
            )
