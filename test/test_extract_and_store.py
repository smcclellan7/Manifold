import unittest
from unittest.mock import Mock
from manifold import extract_and_store
import json
import uuid

payload = {
    'first_name': 'Steve',
    'last_name': 'McClellan',
    'list': [1, 2, 3],
    'location': {
        'state': 'CA',
        'zip_code': 94806
    },
    'other_info': {
        'name_info': {
            'middle_name': 'Martin'
        }
    }
}

data = {
    'first_name': 'Steve',
    'middle_name': 'Martin',
    'last_name': 'McClellan',
    'zip_code': 94806
}


class MyTestCase(unittest.TestCase):
    def test_is_complete(self):
        record = {}
        self.assertFalse(extract_and_store.is_complete(record))
        record['pet'] = 'bird'
        self.assertFalse(extract_and_store.is_complete(record))
        record['first_name'] = 'Steve'
        self.assertFalse(extract_and_store.is_complete(record))
        record['middle_name'] = 'Martin'
        self.assertFalse(extract_and_store.is_complete(record))
        record['last_name'] = 'McClellan'
        self.assertFalse(extract_and_store.is_complete(record))
        record['zip_code'] = 94806
        self.assertTrue(extract_and_store.is_complete(record))

    def test_recursive_extract(self):
        record = {}

        self.assertFalse(extract_and_store.recursive_extract('pet', 'bird', record))
        self.assertEqual(record, {})

        self.assertFalse(extract_and_store.recursive_extract('last_name', 'McClellan', record))
        self.assertEqual(record, {'last_name': 'McClellan'})

        self.assertTrue(extract_and_store.recursive_extract('payload', payload, record))
        self.assertEqual(record, data)

    def test_extract(self):
        record = extract_and_store.extract(payload)
        self.assertEqual(record, data)

    def test_handle(self):
        mock_client = Mock()
        record = extract_and_store.handle(payload, None, mock_client, 'fake-bucket')
        self.assertEqual(record, data)

        mock_client.put_object.assert_called_once()
        args, kwargs = mock_client.put_object.call_args
        body = kwargs['Body']
        bucket_name = kwargs['Bucket']
        key = kwargs['Key']

        self.assertEqual(json.loads(body.decode("utf-8")), data)
        self.assertEqual(bucket_name, 'fake-bucket')
        try:
            uuid.UUID(key)
        except ValueError:
            self.fail('Invalid uuid {}'.format(key))


if __name__ == '__main__':
    unittest.main()
