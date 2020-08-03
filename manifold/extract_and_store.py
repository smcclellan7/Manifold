import boto3
import json
import os
import uuid

s3_client = boto3.client('s3')
bucket_name = os.getenv('BUCKET_NAME')


def extract(payload):
    # TODO implement
    return {
        'first_name': 'Steve',
        'middle_name': 'Martin',
        'last_name': 'McClellan',
        'zip_code': 94806
    }


def handle(event, context):
    data = extract(event)
    j = json.dumps(data)
    b = bytes(j, 'utf-8')
    s3_client.put_object(Body=b, Bucket=bucket_name, Key=str(uuid.uuid4()))
