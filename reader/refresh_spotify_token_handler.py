import json
import logging
import os

from helper.secret_utils import update_secret
from helper.spotify_client import spotify, spotify_refresh_token

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    try:
        refresh_token()
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "hello world",
                # "location": ip.text.replace("\n", "")
            }),
        }
    except Exception as e:
        logger.error(f"Could not refresh token {e}")

        return {
            "statusCode": 402,
            "body": json.dumps({
                "error": e,
                # "location": ip.text.replace("\n", "")
            }),
        }


def refresh_token():
    spotify_auth_manager = spotify.auth_manager
    token_info = spotify_auth_manager.refresh_access_token(spotify_refresh_token)
    update_secret("spotifyRefreshToken", token_info["refresh_token"])
    update_secret("spotifyAccessToken", token_info["access_token"])
    update_secret("spotifyTokenExpiresAt", token_info["expires_at"])
    logger.info(f"Token refreshed!")
