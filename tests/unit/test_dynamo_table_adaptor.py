import unittest
from unittest.mock import MagicMock

from src.adaptor.dynamo_table_adaptor import DynamoTableAdaptor


class DynamoTableAdaptorTest(unittest.TestCase):

    @unittest.mock.patch('boto3.session.Session')
    def test_read_no_items(self, mock_session: MagicMock):
        # arrange
        mock_query = mock_session.return_value.resource.return_value.Table.return_value.query
        mock_query.return_value = {'Items': []}

        # act
        table = DynamoTableAdaptor('table_name', 'pk', 'sk')
        actual_read = table.read(pk_value='1', sk_value='2')

        # assert
        assert actual_read is None
        assert mock_query.call_count == 1
        mock_session.assert_called_with(
            aws_access_key_id='access_key_id',
            aws_secret_access_key='secret_access_key',
            region_name='region'
        )
        mock_session.return_value.resource.assert_called_with(
            service_name='dynamodb'
        )


if __name__ == '__main__':
    unittest.main()
