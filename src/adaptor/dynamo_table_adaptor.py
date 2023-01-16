import os
from typing import Any

import boto3.session as session
from boto3.dynamodb.conditions import Key

_DYNAMO_TABLES: dict[str, object] = {}
_DYNAMO_RESOURCES: dict[str, object] = {}


class DynamoTableAdaptor:
    _aws_access_key_id: str = os.getenv('AWS_ACCESS_KEY_ID')
    _aws_secret_access_key: str = os.getenv('AWS_SECRET_ACCESS_KEY')
    _aws_region: str = os.environ.get('AWS_DEFAULT_REGION')

    def __init__(self, table_name: str, pk_name: str, sk_name: str) -> None:
        self._table_name = table_name
        self._pk_name = pk_name
        self._sk_name = sk_name

    def _get_table(self) -> object:
        """
        Returns a DynamoDB Table Resource with the name `self._table_name` and caches the resource and table in a global
        cache for re-use throughout the application.
        :return: DynamoDB table resource with the name `self._table_name`
        """
        if self._table_name in _DYNAMO_TABLES.keys():
            return _DYNAMO_TABLES[self._table_name]

        dynamodb_resource = session.Session(
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key,
            region_name=self._aws_region
        ).resource(service_name='dynamodb')
        _DYNAMO_RESOURCES[self._table_name] = dynamodb_resource

        table = dynamodb_resource.Table(self._table_name)

        _DYNAMO_TABLES[self._table_name] = table
        return table

    def _create_item(self, pk_value: Any, sk_value=None, extra: dict = None) -> dict[str, Any]:
        """
        Creates a DynamoDB-formatted item dict.
        :param pk_value: Partition key value
        :param sk_value: Sort key value
        :param extra: Dictionary for all other attributes
        :return: DynamoDB-formatted item dict
        """
        if extra is None:
            extra = dict()
        item = {
            self._pk_name: pk_value,
            **extra
        }
        if sk_value is not None:
            item[self._sk_name] = sk_value
        return item

    def read(self, pk_value: Any, sk_value: Any = None) -> dict[str, Any] | list[dict[str, Any]] | None:
        """
        Reads all entries in the respective DynamoDB table which match supplied parameters.
        :param pk_value: Partition key value
        :param sk_value: Sort key value
        :return: None if no entries found, a DynamoDB item dict if one present, or a list of DynamoDB item dicts if
        multiple are present
        """
        expr = Key(self._pk_name).eq(pk_value)
        if sk_value is not None:
            expr &= Key(self._sk_name).eq(sk_value)

        response = self._get_table().query(
                KeyConditionExpression=expr
            )

        return response.get('Items')

    def add_list_item(self, pk_value: Any, sk_value: Any, list_key_name: str = None, list_item: Any = None) -> None:
        """
        Attempts to locate an entry matching the supplied partition and sort key. If an entry is found, appends the
        specified `list_item` to the element in the `list_key_name` column. If an entry is not found, creates a new
        entry with the supplied partition and sort key and a list containing only `list_item` in the `list_key_name`
        column.
        :param pk_value: Partition key value
        :param sk_value: Sort key value
        :param list_key_name: Key name for the column in DynamoDB with a list to be appended to
        :param list_item: Value to be appended to the `list_key_name` column of the matching entry
        """
        existing_entry = self.read(pk_value, sk_value)
        if not existing_entry:
            item = self._create_item(pk_value, sk_value, {list_key_name: [list_item]})
            self._get_table().put_item(Item=item)
        else:
            # TODO make this an update
            existing_entry = existing_entry[0]
            item = self._create_item(pk_value, sk_value)
            self._get_table().delete_item(Key=item)

            item = existing_entry
            if list_key_name not in item or len(item[list_key_name]) < 1:
                item[list_key_name] = []
            item[list_key_name].append(list_item)
            self._get_table().put_item(Item=item)

    def remove_list_item(self, pk_value: Any, sk_value: Any, list_key_name: str, list_item: Any) -> None:
        """
        Attempts to locate an entry matching the supplied partition and sort key. If an entry is found, removes all
        instances of `list_item` from the element in the `list_key_name` column. If after removal of all such instances
        the list at the specified entry is empty, removes the entry from the DynamoDB table.
        :param pk_value: Partition key value
        :param sk_value: Sort key value
        :param list_key_name: Key name for the column in DynamoDB with a list to be appended to
        :param list_item: Value to be appended to the `list_key_name` column of the matching entry
        """
        item = self._create_item(pk_value, sk_value)

        existing_entry = self.read(pk_value, sk_value)
        if existing_entry is None:
            # TODO notify / error handle
            return
        existing_entry = existing_entry[0]

        if list_item is None:
            self._get_table().delete_item(Key=item)
        else:
            list_item_value = [elem for elem in existing_entry.get(list_key_name, []) if elem != list_item]

            self._get_table().delete_item(Key=item)
            if len(list_item_value) > 0:
                item[list_key_name] = list_item_value
                self._get_table().put_item(Item=item)

    def delete(self, pk_value: Any, sk_value: Any = None) -> None:
        """
        Deletes all entries in the respective DynamoDB table which match supplied parameters.
        :param pk_value: Partition key value
        :param sk_value: Sort key value
        """
        item = self._create_item(pk_value, sk_value)

        self._get_table().delete_item(Key=item)
