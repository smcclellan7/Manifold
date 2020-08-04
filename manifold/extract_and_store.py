import boto3
import json
import os
import uuid
from datetime import datetime


def is_complete(record):
    """Checks if a record contains a complete set of fields.

    :param record: the record being constructed
    :type record: dict
    :return: True if the record contains all name and zip code fields, False otherwise
    :rtype: bool
    """
    return 'first_name' in record and \
           'middle_name' in record and \
           'last_name' in record and \
           'zip_code' in record


def recursive_extract(name, value, record):
    """Extracts data from a JSON field (as name/value pair) and stores it in a record. Recursively processes sub-fields.

    :param name: the name of the JSON field
    :param value: the value of the JSON field
    :param record: the record to store any discovered data
    :type name: str
    :type value: dict, list, str, int, long, float
    :type record: dict
    :return: True if the record is complete after processing the given field, False otherwise
    :rtype: bool
    """
    if isinstance(value, dict):
        for n, v in value.items():
            if recursive_extract(n, v, record):
                return True
    elif isinstance(value, str):
        if name == 'first_name':
            record['first_name'] = str(value)
            if is_complete(record):
                return True
        elif name == 'middle_name':
            record['middle_name'] = str(value)
            if is_complete(record):
                return True
        elif name == 'last_name':
            record['last_name'] = str(value)
            if is_complete(record):
                return True
    elif isinstance(value, int):
        if name == 'zip_code':
            record['zip_code'] = int(value)
            if is_complete(record):
                return True
    return False


def extract(payload):
    """Extracts name and zip code fields from a JSON payload.

    Fields can be found at any level within the JSON structure. Lists are not traversed. If more than one field with a
    given name exists within the structure, it is undefined which field will be used.

    :param payload: a JSON record to be searched
    :type payload: dict
    :return: a record containing only the name and zip code fields
    :rtype: dict
    """
    record = {}
    for n, v in payload.items():
        if recursive_extract(n, v, record):
            return record
    return record


def key(event):
    epoch_time = event['requestContext']['requestTimeEpoch']
    date_prefix = datetime.utcfromtimestamp(epoch_time).strftime('%Y/%m/%d')
    unique_id = str(uuid.uuid4())
    return date_prefix + '/' + unique_id


def handle(event, context, s3_client=boto3.client('s3'), bucket_name=os.getenv('BUCKET_NAME')):
    """Entry-point for the ExtractAndStore Lambda.

    Extracts name and zip code fields from a JSON payload and stores them in an S3 bucket. Bucket records are keyed with
    a random UUID.

    :param event: the incoming request object from the HTTP endpoint
    :param context: the request context
    :param s3_client: an S3 client for storing the extracted data
    :param bucket_name: the name of the S3 bucket where the extracted data should be stored
    :type event: dict
    :type bucket_name: str
    :return: the extracted data, or an error record if the request was bad
    :rtype: dict
    """
    data = extract(json.loads(event['body']))
    if len(data) == 0:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'Request did not contain any name or zip code fields'
        }
    j = json.dumps(data)
    b = bytes(j, 'utf-8')
    s3_client.put_object(Body=b, Bucket=bucket_name, Key=key(event))
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': j
    }
