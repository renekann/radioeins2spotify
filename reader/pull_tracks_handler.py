import json
import logging

from models.track import Track
from services.tracks_service import get_tracks, publish_new_tracks, store_pulled_tracks, filter_for_new_tracks
from helper.bucket_client import load
from helper.utils import generate_radioeins_url

url_today = generate_radioeins_url(days_to_subtract=0)
url_day_before = generate_radioeins_url(days_to_subtract=1)
url_two_days_before = generate_radioeins_url(days_to_subtract=2)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    try:
        tracks = []
        tracks += get_tracks(url_today)

        tracks.sort(key=lambda x: x.playtime, reverse=False)

        old_tracks = [Track(**d) for d in json.loads(load('pulled_tracks.json'))]
        unique_new_tracks = filter_for_new_tracks(tracks, old_tracks)

        if len(unique_new_tracks) > 0:
            store_pulled_tracks(tracks, name='pulled_tracks.json')
            publish_new_tracks(unique_new_tracks)
            logger.info(f"Published new unique tracks: {len(unique_new_tracks)}")
        else:
            logger.info(f"Published no new unique tracks.")

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

        if len(unique_new_tracks) > 0:
            store_pulled_tracks(tracks, name='older_pulled_tracks.json')
            publish_new_tracks(unique_new_tracks)
            logger.info(f"Published new unique older tracks: {len(unique_new_tracks)}")
        else:
            logger.info(f"Published no older unique tracks.")

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
