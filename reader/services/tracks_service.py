import json
import logging
import os
from json import JSONDecodeError

import boto3
import requests

from env import TRACKS_TABLE_NAME
from models.track import Track
from helper.bucket_client import store, load

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_tracks(url):
    try:
        response = requests.get(url)

        if response.status_code != 200:
            logger.error(f"Could not fetch from url {url}, response was {response.status_code}")
            return []

        tracks = response.json()

        if tracks is None:
            logger.error(f"Could not decode from url {url}, response was not json?")
            return []

        filtered_tracks = list(filter(lambda x: (("k3" in x and x['k3'] == "S") or ("k3" not in x)), tracks["data"]))
        mapped_tracks = list(map(lambda x: Track(playtime=x["s"], artist=x["k1"], title=x["k2"]), filtered_tracks))
        return mapped_tracks

    except JSONDecodeError as e:
        logger.warning(
            f"Could not fetch from url {url}, response was {response.status_code}, body is not json decodable? (Response {response.content})?")
        return []
    except Exception as e:
        logger.error(
            f"Could not fetch from url {url}, response status was {response.status_code}, body response {response.content})")
        raise e


def store_pulled_tracks(tracks, name='pulled_tracks.json'):
    json_string = json.dumps(tracks, default=lambda x: x.__dict__)
    store(json_string, name)


def filter_for_new_tracks(new_tracks, old_tracks):
    unique_new_tracks = set(new_tracks) - set(old_tracks)
    return unique_new_tracks


def publish_new_tracks(tracks):
    for track in tracks:
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=track.toJson(), MessageGroupId="NewTrack")


def create(track: Track):
    tracks_table = dynamodb.Table(TRACKS_TABLE_NAME)
    response = tracks_table.put_item(
        Item={
            "id": track.hash,
            "artist": track.artist,
            "spotifyId": track.spotifyId,
            "plays": [track.playtime],
            "title": track.title
        }
    )

    return response


def update_playtime_for_track(hash, playtime):
    tracks_table = dynamodb.Table(TRACKS_TABLE_NAME)
    response = tracks_table.update_item(
        Key={
            'id': hash
        },
        UpdateExpression='set plays=list_append(plays,:playtime)',
        ExpressionAttributeValues={
            ':playtime': [playtime]
        },
        ReturnValues="UPDATED_NEW"
    )

    return response


def update_spotifyid_for_track(hash, spotify_id):
    tracks_table = dynamodb.Table(TRACKS_TABLE_NAME)
    response = tracks_table.update_item(
        Key={
            'id': hash
        },
        UpdateExpression='set spotifyId=:spotify_id',
        ExpressionAttributeValues={
            ':spotify_id': spotify_id
        },
        ReturnValues="UPDATED_NEW"
    )

    return response


def search(track):
    tracks_table = dynamodb.Table(TRACKS_TABLE_NAME)
    response = tracks_table.get_item(
        Key={
            'id': track.hash
        }
    )

    return response.get('Item')
