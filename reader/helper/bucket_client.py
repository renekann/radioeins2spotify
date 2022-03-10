import logging

import boto3
from env import BUCKET_NAME

s3 = boto3.client('s3')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def store(data, key):
    s3.put_object(Body=data, Bucket=BUCKET_NAME, Key=key)


def load(key):
    response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    content = response['Body'].read().decode('utf8')
    return content


