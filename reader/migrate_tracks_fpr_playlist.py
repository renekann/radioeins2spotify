import json
import logging
import os

from services.spotify_service import handle_track, get_playlist_tracks
from models.track import Track

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        tracks = get_playlist_tracks("20FglkPfZOKbcLG2zOZRHA", 0, 50)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "hello world",
                # "location": ip.text.replace("\n", "")
            }),
        }
    except Exception as e:
        logger.error(f"Could not handle track {e}")

        return {
            "statusCode": 402,
            "body": json.dumps({
                "error": e,
                # "location": ip.text.replace("\n", "")
            }),
        }