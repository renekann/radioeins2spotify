import json
import logging
import datetime

from services.tracks_service import get_tracks, publish_new_tracks

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

        publish_new_tracks(tracks)
        logger.info(f"Published recent tracks: {len(tracks)}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "hello world",
                # "location": ip.text.replace("\n", "")
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


def handlerOlderTracks(event, context):
    try:
        tracks = []
        tracks += get_tracks(url_day_before)
        tracks += get_tracks(url_two_days_before)

        tracks.sort(key=lambda x: x.playtime, reverse=False)

        publish_new_tracks(tracks)
        logger.info(f"Pulled and published older tracks: {len(tracks)}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "hello world",
                # "location": ip.text.replace("\n", "")
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