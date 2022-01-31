import os
from hashlib import sha1

import boto3

from env import PLAYLIST_TRACKS_TABLE_NAME
from models.track import Track

dynamodb = boto3.resource('dynamodb')
playlists_tracks_table = dynamodb.Table(PLAYLIST_TRACKS_TABLE_NAME)


def add(track: Track, playlist_id):
    entry_id = sha1(str(f"{track.hash}-{playlist_id}").encode('utf-8')).hexdigest()

    response = playlists_tracks_table.put_item(
        Item={
            "id": entry_id,
            "track_hash": track.hash,
            "playlist_id": playlist_id
        }
    )

    return response


def in_playlist(track, playlist_id):
    response = playlists_tracks_table.get_item(
        Key={
            'track_hash': track.hash,
            'playlist_id': playlist_id
        }
    )

    if "Item" in response:
        return response.get('Item')
    else:
        return None
