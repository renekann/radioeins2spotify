import logging
import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from utils.secret_utils import get_secret

slackBotToken = get_secret("slackBotToken")
slackChannel = os.environ['SLACK_CHANNEL']

slackClient = WebClient(token=slackBotToken)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def send_slack_message(message, channel=slackChannel):
    try:
        response = slackClient.chat_postMessage(channel=channel, text=message)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        logger.error(f"Got an error: {e.response['error']}")
