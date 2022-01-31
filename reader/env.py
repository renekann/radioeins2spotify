import os
from dotenv import load_dotenv
load_dotenv()

STAGE = os.environ.get('STAGE')
TRACKS_TABLE_NAME = os.environ.get('TRACKS_TABLE_NAME')
PLAYLIST_TABLE_NAME = os.environ.get('PLAYLIST_TABLE_NAME')
QUEUE_URL = os.environ.get('QUEUE_URL')
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
PLAYLIST_PREFIX = os.environ.get('PLAYLIST_PREFIX')
PLAYLIST_TRACKS_TABLE_NAME = os.environ.get('PLAYLIST_TRACKS_TABLE_NAME')
MAX_NUMBER_TRACKS_IN_PLAYLIST = os.environ.get('MAX_NUMBER_TRACKS_IN_PLAYLIST')