from datetime import datetime
import logging

import boto3
import os

from env import TRACKS_TABLE_NAME, PLAYLIST_TABLE_NAME, QUEUE_URL, MAX_NUMBER_TRACKS_IN_PLAYLIST
from services.playlist_service import get_current_playlist, create_playlist, delete_current_playlist
from helper.slack import send_slack_message
from helper.spotify_client import spotify, spotify_playlist_name_prefix
from services.playlist_tracks_service import in_playlist, add
from services.tracks_service import update_spotifyid_for_track, search, create, update_playtime_for_track

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client('sqs')

dynamodb = boto3.resource('dynamodb')
tracks_table = dynamodb.Table(TRACKS_TABLE_NAME)
playlists_table = dynamodb.Table(PLAYLIST_TABLE_NAME)


def handle_track(track, receipt_handle):
    is_new = is_new_track(track)

    if not is_new:
        logger.info(f"[NOT_NEW] Remove {track}, because track is already handled")
        sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)
        return

    if track.spotifyId == "":
        updated_track = search_for_spotify_id(track)

        if updated_track is None:
            # TODO: requeue with flag to search with other query
            logger.info(f"[NO_SPOTIFY_ID] Remove {track}, because no spotifyId could be fetched")
            sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)
            return
        else:
            track = updated_track
            update_spotifyid_for_track(track.hash, track.spotifyId)

    current_playlist_id = get_or_create_current_playlist()
    logger.info(f"PlaylistId: {current_playlist_id}")

    already_in_playlist = in_playlist(track=track, playlist_id=current_playlist_id)

    if already_in_playlist is False:
        logger.info(f"[ADDED] Add {track} to {current_playlist_id}")
        add_track_to_playlist(track=track, playlist_id=current_playlist_id)
    else:
        logger.info(f"[NOT_ADDED] {track} already in {current_playlist_id}")

    sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)


def is_new_track(track):
    existing_track = search(track)

    if existing_track is None:
        logger.info(f"[DOES NOT EXIST] create {track}")
        create(track)
        return True
    else:
        plays = existing_track["plays"]

        logger.info(f"[PLAYS] {plays} for {track}")

        if track.playtime not in plays:
            update_playtime_for_track(track.hash, track.playtime)
            track.spotifyId = existing_track["spotifyId"]
            logger.info(f"[NOT IN PLAYS] {track} with {track.playtime}")
            return True
        else:
            logger.info(f"[IN PLAYS] {track} with {track.playtime}")

            if existing_track["spotifyId"] is None:
                return True

    return False


def search_for_spotify_id(track):
    search_string = track.searchString()
    result = spotify.search(q=search_string, limit=1)

    if "tracks" in result and len(result["tracks"]["items"]) > 0:
        track.spotifyId = result["tracks"]["items"][0]["id"]
        logger.info(f"[FOUND SPOTIFY ID] Found spotifyId for {track}: {track.spotifyId}")
        return track
    else:
        logger.info(
            f"[NOT FOUND SPOTIFY ID]  Could not find spotifyId for: {track} with search string: {search_string}")
        return None


def get_or_create_current_playlist():
    current_playlist_id = get_current_playlist()

    if current_playlist_id is None:
        date = datetime.now().strftime("%d-%m-%Y")
        playlist_name = f"{spotify_playlist_name_prefix} (since {date})"

        user_id = spotify.me()['id']
        result = spotify.user_playlist_create(user=user_id, name=playlist_name)

        if result is not None:
            send_slack_message(f"New Playlist created: {result['external_urls']['spotify']}")
            create_playlist(result["id"])
        else:
            logger.error(f"Could not create a playlist with result: {result}")
            raise CouldNotCreatePlaylistException(message=f"Could not create a playlist with result {result}")

        return result["id"]
    else:
        result = spotify.playlist(playlist_id=current_playlist_id)
        number_of_tracks = 0

        if result is not None and result.get('tracks') is not None:
            number_of_tracks = result.get('tracks').get('total')

        if number_of_tracks >= int(MAX_NUMBER_TRACKS_IN_PLAYLIST):
            logger.info(f"Max number of tracks in playlist {current_playlist_id} reached - create new.")
            result = None

        if result is not None:
            return current_playlist_id
        else:
            delete_current_playlist()
            logger.info(f"Could not find playlist with id {current_playlist_id}, create new one.")
            return get_or_create_current_playlist()


def get_playlist_tracks(playlist_id, start=0, limit=50, stop_at=-1):
    playlist_tracks = []
    result = spotify.playlist_items(playlist_id=playlist_id)

    if "items" in result:
        playlist_tracks += result["items"]

    if result["next"] is not None:

        stop = False
        offset = limit
        current_offset = start

        while not stop:
            result = spotify.playlist_items(playlist_id=playlist_id, offset=current_offset, limit=limit)

            if result["next"] is None or 0 < stop_at <= current_offset:
                stop = True

            playlist_tracks += result["items"]
            current_offset += offset

    return playlist_tracks


# def already_in_playlist(track, playlist_tracks):
#     filtered_tracks = list(filter(lambda x: ("track" in x and x['track']["id"] == track.spotifyId), playlist_tracks))
#     return len(filtered_tracks) > 0


def add_track_to_playlist(track, playlist_id):
    result = spotify.playlist_add_items(playlist_id=playlist_id, items=[track.spotifyId])

    if result["snapshot_id"] is not None:
        add(track=track, playlist_id=playlist_id)
        send_slack_message(f"{track} added to {playlist_id}", channel="radio2spotify-app-prod-log")
        logger.info(f"[TRACK ADDED TO PLAYLIST] {track} added to {playlist_id} ({result})")
    else:
        logger.error(f"[TRACK NOT ADDED] {track} not added to {playlist_id} ({result})")


class Error(Exception):
    def __init__(self, message):
        self.message = message


class SpotifyIdNotFoundException(Error):
    pass


class CouldNotCreatePlaylistException(Error):
    pass
