import unittest
from unittest.mock import Mock
from manifold import extract_and_store
from datetime import datetime
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

event = {
    'body': json.dumps(payload),
    'requestContext': {
        'requestTimeEpoch': int(datetime(1986, 7, 18, 9, 15, 0).timestamp() * 1e3)
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

    def test_key(self):
        key = extract_and_store.key(event)
        path = key.split('/')
        self.assertEqual(len(path), 4)
        self.assertEqual(path[0], 'year=1986')
        self.assertEqual(path[1], 'month=07')
        self.assertEqual(path[2], 'day=18')

        parts = path[3].split('.')
        self.assertEqual(len(parts), 2)
        try:
            uuid.UUID(parts[0])
        except ValueError:
            self.fail('Invalid uuid {}'.format(parts[0]))
        self.assertEqual(parts[1], 'json')

    def test_handle(self):
        mock_client = Mock()
        resp = extract_and_store.handle(event, None, mock_client, 'fake-bucket')
        self.assertEqual(resp['statusCode'], 200)
        self.assertEqual(resp['headers']['Content-Type'], 'text/plain')
        resp_body = resp['body']

        mock_client.put_object.assert_called_once()
        args, kwargs = mock_client.put_object.call_args
        body = kwargs['Body']
        bucket_name = kwargs['Bucket']
        key = kwargs['Key']

        self.assertEqual(json.loads(body.decode("utf-8")), data)
        self.assertEqual(bucket_name, 'fake-bucket')
        self.assertEqual(resp_body, key)

    def test_handle_no_data(self):
        bad_req = {'body': json.dumps({'favorite_color': 'green'})}
        bad_resp = extract_and_store.handle(bad_req, None, None, 'fake-bucket')
        self.assertEqual(bad_resp['statusCode'], 400)


if __name__ == '__main__':
    unittest.main()
