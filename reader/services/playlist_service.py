import os
import boto3

from env import PLAYLIST_TABLE_NAME

dynamodb = boto3.resource('dynamodb')
playlists_table = dynamodb.Table(PLAYLIST_TABLE_NAME)


def get_current_playlist():
    response = playlists_table.get_item(
        Key={
            'id': 'current'
        }
    )

    if response.get('Item') is not None:
        return response.get('Item').get('playlist_id')
    else:
        return None


def create_playlist(playlist_id):
    response = playlists_table.put_item(
        Item={
            "id": 'current',
            "playlist_id": playlist_id
        }
    )

    return response


def delete_current_playlist():
    response = playlists_table.delete_item(
        Key={
            "id": 'current'
        }
    )

    return response
