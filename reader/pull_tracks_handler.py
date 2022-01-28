import json
import logging
import datetime

from models.track import Track
from services.tracks_service import get_tracks, publish_new_tracks, store_pulled_tracks, filter_for_new_tracks
from helper.bucket_client import load

url_today = 'http://rbb-radio1.konsole-labs.com/backend/get/?typ=playlist&subtyp=&ver=1525362457d&av=2.2.3'
url_day_before = 'http://rbb-radio1.konsole-labs.com/backend/get/get-playlist-day.php?dayback=1'
url_two_days_before = 'http://rbb-radio1.konsole-labs.com/backend/get/get-playlist-day.php?dayback=2'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        tracks = []
        tracks += get_tracks(url_today)

        tracks.sort(key=lambda x: x.playtime, reverse=False)

        old_tracks = [Track(**d) for d in json.loads(load('pulled_tracks.json'))]
        unique_new_tracks = filter_for_new_tracks(tracks, old_tracks)
        store_pulled_tracks(tracks, name='pulled_tracks.json')

        publish_new_tracks(unique_new_tracks)
        logger.info(f"Published new unique tracks: {len(unique_new_tracks)}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "hello world"
            }),
        }
    except Exception as e:
        logger.error(f"Could not fetch tracks {e}")

        return {
            "statusCode": 402,
            "body": json.dumps({
                "error": e
            }),
        }


def handlerOlderTracks(event, context):
    try:
        tracks = []
        tracks += get_tracks(url_day_before)
        tracks += get_tracks(url_two_days_before)

        tracks.sort(key=lambda x: x.playtime, reverse=False)

        old_tracks = [Track(**d) for d in json.loads(load('older_pulled_tracks.json'))]
        unique_new_tracks = filter_for_new_tracks(tracks, old_tracks)
        store_pulled_tracks(tracks, name='older_pulled_tracks.json')

        publish_new_tracks(unique_new_tracks)
        logger.info(f"Published new unique older tracks: {len(unique_new_tracks)}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "hello world"
            }),
        }
    except Exception as e:
        logger.error(f"Could not fetch tracks {e}")

        return {
            "statusCode": 402,
            "body": json.dumps({
                "error": e,
                # "location": ip.text.replace("\n", "")
            }),
        }