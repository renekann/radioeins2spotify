import boto3
import os

s3 = boto3.client('s3')


def store(data, key):
    bucket = os.environ["BUCKET_NAME"]
    s3.put_object(Body=data, Bucket=bucket, Key=key)


def load(key):
    bucket = os.environ["BUCKET_NAME"]
    try:
        response = s3.get_object(bucket, key)
        # Read data from response.
    finally:
        response.close()
        response.release_conn()
