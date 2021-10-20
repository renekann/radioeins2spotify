from datetime import datetime
import logging

import boto3
import os

from services.playlist_service import get_current_playlist, create_playlist, delete_current_playlist
from utils.slack import send_slack_message
from utils.spotify_client import spotify, spotify_playlist_name_prefix
from services.tracks_service import update_spotifyid_for_track, search, create, update_playtime_for_track

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client('sqs')

dynamodb = boto3.resource('dynamodb')
tracks_table = dynamodb.Table(os.environ["TRACKS_TABLE_NAME"])
playlists_table = dynamodb.Table(os.environ["PLAYLIST_TABLE_NAME"])

def handle_track(track, receipt_handle):

    is_new = is_new_track(track)

    if not is_new:
        logger.info(f"[NOT_NEW] Remove {track}, because track is already handled")
        sqs.delete_message(QueueUrl=os.environ['QUEUE_URL'], ReceiptHandle=receipt_handle)
        return

    if track.spotifyId == "":
        updated_track = search_for_spotify_id(track)

        if updated_track == None:
            # TODO: requeue with flag to search with other query
            logger.warning(f"[NO_SPOTIFY_ID] Remove {track}, because no spotifyId could be fetched")
            sqs.delete_message(QueueUrl=os.environ['QUEUE_URL'], ReceiptHandle=receipt_handle)
            return
        else:
            track = updated_track
            update_spotifyid_for_track(track.hash, track.spotifyId)

    current_playlist_id = get_or_create_current_playlist()
    logger.debug(f"PlaylistId: {current_playlist_id}")

    playlistTracks = get_playlist_tracks(current_playlist_id)

    if (already_in_playlist(track, playlistTracks) == False):
        logger.info(f"[ADDED] Add {track} to {current_playlist_id}")
        add_track_to_playlist(track=track, playlistId=current_playlist_id)
    else:
        logger.info(f"[NOT_ADDED] {track} already in {current_playlist_id}")

    sqs.delete_message(QueueUrl=os.environ['QUEUE_URL'], ReceiptHandle=receipt_handle)


def is_new_track(track):
    existing_track = search(track)

    if(existing_track == None):
        create(track)
        return True
    else:
        plays = existing_track["plays"]

        if (track.playtime not in plays):
            update_playtime_for_track(track.hash, track.playtime)
            track.spotifyId = existing_track["spotifyId"]
            return True

    return False

def search_for_spotify_id(track):
    result = spotify.search(q=track.searchString(), limit=1)

    if "tracks" in result and len(result["tracks"]["items"]) > 0:
        track.spotifyId = result["tracks"]["items"][0]["id"]
        logger.debug(f"Found spotifyId for {track}: {track.spotifyId}")
        return track
    else:
        logger.warning(f"Could not find spotifyId for: {track}")
        return None


def get_or_create_current_playlist():
    current_playlist_id = get_current_playlist()

    if (current_playlist_id == None):
        date = datetime.now().strftime("%d-%m-%Y")
        playlist_name = f"{spotify_playlist_name_prefix} (since {date})"

        user_id = spotify.me()['id']
        result = spotify.user_playlist_create(user=user_id, name=playlist_name)

        if (result != None):
            send_slack_message(f"New Playlist created: {result['external_urls']['spotify']}")
            create_playlist(result["id"])
        else:
            logger.error(f"Could not create a playlist with result: {result}")
            raise CouldNotCreatePlaylistException(message=f"Could not create a playlist with result {result}")

        return result["id"]
    else:
        result = spotify.playlist(playlist_id=current_playlist_id)
        number_of_tracks = 0

        if result != None and result.get('tracks') is not None:
            number_of_tracks = result.get('tracks').get('total')

        if number_of_tracks >= int(os.environ['MAX_NUMBER_TRACKS_IN_PLAYLIST']):
            logger.debug(f"Max number of tracks in playlist {current_playlist_id} reached - create new.")
            result = None

        if (result != None):
            return current_playlist_id
        else:
            delete_current_playlist()
            logger.warning(f"Could not find playlist with id {current_playlist_id}, create new one.")
            return get_or_create_current_playlist()


def get_playlist_tracks(playlist_id):
    playlistTracks = []
    result = spotify.playlist_items(playlist_id=playlist_id)

    if "items" in result:
        playlistTracks += result["items"]

    if result["next"] != None:

        stop = False
        offset = 100
        currentOffset = offset

        while stop == False:
            result = spotify.playlist_items(playlist_id=playlist_id, offset=currentOffset)

            if result["next"] is None:
                stop = True

            playlistTracks += result["items"]
            currentOffset += offset

    return playlistTracks


def already_in_playlist(track, playlistTracks):
    filtered_tracks = list(filter(lambda x: ("track" in x and x['track']["id"] == track.spotifyId), playlistTracks))
    return len(filtered_tracks) > 0


def add_track_to_playlist(track, playlistId):
    result = spotify.playlist_add_items(playlist_id=playlistId, items=[track.spotifyId])
    logger.debug(result)

class Error(Exception):
    def __init__(self, message):
        self.message = message


class SpotifyIdNotFoundException(Error):
    pass


class CouldNotCreatePlaylistException(Error):
    pass
