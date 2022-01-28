import boto3
import json

secret_name = "radio2spotify"
region_name = "eu-central-1"
secrets_client = boto3.client("secretsmanager")


def get_secret(name):
    response = secrets_client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response.get('SecretString')).get(name)
    return secret


def update_secret(name, value):
    response = secrets_client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response.get('SecretString'))
    secret[name] = value
    updated_secret = secrets_client.update_secret(SecretId=secret_name, SecretString=json.dumps(secret))
    return updated_secret
