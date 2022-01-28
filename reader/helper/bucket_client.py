import logging

import boto3
import os
from botocore.client import Config

s3 = boto3.client('s3')

# s3 = boto3.client('s3',
#                     endpoint_url='http://localhost:9000',
#                     aws_access_key_id='test',
#                     aws_secret_access_key='testtest',
#                     config=Config(signature_version='s3v4'),
#                     region_name='us-east-1')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def store(data, key):
    bucket = os.environ["BUCKET_NAME"]
    s3.put_object(Body=data, Bucket=bucket, Key=key)


def load(key):
    bucket = os.environ["BUCKET_NAME"]
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf8')
    return content


