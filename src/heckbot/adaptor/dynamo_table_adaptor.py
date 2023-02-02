from __future__ import annotations

import os
from typing import Optional
from typing import TypeVar
from weakref import WeakValueDictionary

import boto3.session as session
from boto3.dynamodb.conditions import ConditionBase
from boto3.dynamodb.conditions import Key
from boto3.resources.base import ServiceResource
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table

_DYNAMO_TABLES: WeakValueDictionary[str, Table] = WeakValueDictionary()
_DYNAMO_RESOURCES: WeakValueDictionary[str, ServiceResource] = \
    WeakValueDictionary()


class DynamoTableAdaptor:
    """
    Adaptor service for transferring data between the application and a
    composite-key DynamoDB table.
    """
    _aws_access_key_id: str = os.getenv('AWS_ACCESS_KEY_ID', '')
    _aws_secret_access_key: str = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    _aws_region: str = os.environ.get('AWS_DEFAULT_REGION', '')

    DynamoItem = TypeVar('DynamoItem')

    def __init__(
            self,
            table_name: str,
            pk_name: str,
            sk_name: str,
    ) -> None:
        """
        Constructor method
        :param table_name: Logical name of the table in DynamoDB
        :param pk_name: Name of the partition_key in the DynamoDB table
        :param sk_name: Name of the sort key in the DynamoDB table
        """
        self._table_name: str = table_name
        self._pk_name: str = pk_name
        self._sk_name: str = sk_name

    def _get_table(
            self,
    ) -> Table:
        """
        Returns a DynamoDB Table Resource with the name
        `self._table_name` and caches the resource and table in a global
        cache for re-use throughout the application.
        :return: DynamoDB table resource with the name
        `self._table_name`
        """
        if self._table_name in _DYNAMO_TABLES.keys():
            return _DYNAMO_TABLES[self._table_name]

        dynamodb_resource: DynamoDBServiceResource = session.Session(
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key,
            region_name=self._aws_region,
        ).resource(service_name='dynamodb')
        _DYNAMO_RESOURCES[self._table_name] = dynamodb_resource

        table: Table = dynamodb_resource.Table(self._table_name)

        _DYNAMO_TABLES[self._table_name] = table
        return table

    def _fmt_item(
            self,
            pk_value: DynamoItem,
            sk_value: Optional[DynamoItem] = None,
            extra: Optional[dict] = None,
    ) -> dict[str, DynamoItem]:
        """
        Creates a DynamoDB-formatted item dict.
        :param pk_value: Partition key value
        :param sk_value: Sort key value
        :param extra: Dictionary for all other attributes
        :return: DynamoDB-formatted item dict
        """
        if extra is None:
            extra = {}
        item = {
            self._pk_name: pk_value,
            **extra,
        }
        if sk_value is not None:
            item[self._sk_name] = sk_value
        return item

    def read(
            self,
            pk_value: DynamoItem,
            sk_value: Optional[DynamoItem] = None,
    ) -> Optional[list[dict[str, DynamoItem]]]:
        """
        Reads all entries in the respective DynamoDB table which match
        supplied parameters.
        :param pk_value: Partition key value
        :param sk_value: Sort key value
        :return: a list of DynamoDB item dicts
        """
        expr: ConditionBase = Key(self._pk_name).eq(pk_value)
        if sk_value is not None:
            expr &= Key(self._sk_name).eq(sk_value)

        response = self._get_table().query(KeyConditionExpression=expr)

        return response.get('Items', [])

    def add_list_item(
            self,
            pk_value: DynamoItem,
            sk_value: DynamoItem,
            list_name: Optional[str] = None,
            item: Optional[DynamoItem] = None,
    ) -> None:
        """
        Attempts to locate an entry matching the supplied partition and
        sort key. If an entry is found, appends the specified
        `item` to the element in the `list_name` column. If an
        entry is not found, creates a new entry with the supplied
        partition and sort key and a list containing only `item`
        in the `list_name` column.
        :param pk_value: Partition key value
        :param sk_value: Sort key value
        :param list_name: Key name for the column in DynamoDB with a
        list to be appended to
        :param item: Value to be appended to the `list_name`
        column of the matching entry
        """
        result = self._get_table().update_item(
            Key=self._fmt_item(pk_value, sk_value),
            UpdateExpression=(
                f'SET {list_name} = list_append(if_not_exists({list_name}, :empty_list), :i'
            ),
            ExpressionAttributeValues={
                ':i': [item],
                ':empty_list': [],
            },
            ReturnValues='UPDATED_NEW',
        )
        if result['ResponseMetadata']['HTTPStatusCode'] == 200 and 'Attributes' in result:
            return result['Attributes']['some_attr']

    def remove_list_item(
            self,
            pk_value: DynamoItem,
            sk_value: DynamoItem,
            list_name: str,
            item: DynamoItem,
    ) -> None:
        """
        Attempts to locate an entry matching the supplied partition and
        sort key. If an entry is found, removes all instances of
        `item`  from the element in the `list_name` column. If
        after removal of all such instances the list at the specified
        entry is empty, removes the entry from the DynamoDB table.
        :param pk_value: Partition key value
        :param sk_value: Sort key value
        :param list_name: Key name for the column in DynamoDB with a
        list to be appended to
        :param item: Value to be appended to the `list_name`
        column of the matching entry
        """
        # TODO implement
        raise NotImplementedError

    def delete(
            self,
            pk_value: DynamoItem,
            sk_value: Optional[DynamoItem] = None,
    ) -> None:
        """
        Deletes all entries in the respective DynamoDB table which match
        supplied parameters.
        :param pk_value: Partition key value
        :param sk_value: Sort key value
        """
        self._get_table().delete_item(
            Key=self._fmt_item(pk_value, sk_value),
        )
