import json
import logging
import os

from services.spotify_service import handle_track
from models.track import Track

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    try:
        for record in event['Records']:
            track = json.loads(record["body"], object_hook=lambda d: Track(**d))
            receipt_handle = record["receiptHandle"]
            handle_track(track, receipt_handle)

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