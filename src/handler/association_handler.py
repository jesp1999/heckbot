from src.adaptor.dynamo_table_adaptor import DynamoTableAdaptor


class AssociationHandler:
    _association_table = DynamoTableAdaptor('HeckBotAssociations', 'Server', 'Pattern')

    def get_all_associations(self, server):
        results = self._association_table.read(
            pk_value=server
        )
        if results is None:
            return {}

        associations = {result['Pattern']: result['Reactions'] for result in results}
        return associations

    def get_associations_for_pattern(self, server, pattern):
        return self._association_table.read(
            pk_value=server,
            sk_value=pattern
        )[0].get('Reactions')

    def add_association(self, server, word, emoji):
        self._association_table.add_list_item(
            pk_value=server,
            sk_value=word,
            list_key_name='Reactions',
            list_item=emoji
        )

    def remove_association(self, server, word, emoji=None):
        self._association_table.remove_list_item(
            pk_value=server,
            sk_value=word,
            list_key_name='Reactions',
            list_item=emoji
        )
