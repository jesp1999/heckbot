import os

import boto3.session as session
import dotenv
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv

_DYNAMO_TABLES = {}
_DYNAMO_RESOURCES = {}


class DynamoTableAdaptor:
    _aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    _aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    _aws_region = os.environ.get('AWS_DEFAULT_REGION')

    def __init__(self, table_name, pk_name, sk_name=None):
        self._table_name = table_name
        self._pk_name = pk_name
        self._sk_name = sk_name

    def _get_table(self):
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

    def _create_item(self, pk_value, sk_value=None, extra: dict = None):
        if extra is None:
            extra = dict()
        item = {
            self._pk_name: pk_value,
            **extra
        }
        if sk_value is not None:
            item[self._sk_name] = sk_value
        return item

    def _validate_item(self, item: dict):
        assert self._pk_name in item.keys()
        # assert self._sk_name in item.keys()

    def read(self, pk_value, sk_value=None):
        expr = Key(self._pk_name).eq(pk_value)
        if sk_value is not None:
            expr &= Key(self._sk_name).eq(sk_value)

        response = self._get_table().query(
                KeyConditionExpression=expr
            )

        if 'Items' not in response or len(response['Items']) < 1:
            return None

        return response['Items']

    def add_list_item(self, pk_value, sk_value=None, list_key_name: str = None, list_item=None):
        existing_entry = self.read(pk_value, sk_value)
        if existing_entry is None:
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


    # TODO clean up this method signature
    def remove_list_item(self, pk_value, sk_value=None, list_key_name: str = None, list_item=None):
        item = self._create_item(pk_value, sk_value)
        self._validate_item(item)

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
