import re
from datetime import datetime, timedelta
from env import STAGE
import pytz


def remove_words_from_string(value, stopwords, replace=""):
    replaced_value = value
    for word in stopwords:
        replaced_value = replaced_value.replace(word, replace)

    replaced_value = re.sub("\s\s+", " ", replaced_value)

    return replaced_value


def isDevStage():
    if STAGE:
        return STAGE == 'dev'
    else:
        return False


def generate_radioeins_url(days_to_subtract=0):
    url = "http://rbb-cache-1.konsole-labs.com/radioeins/playlist/get/program-day.php?idStation=3&d="
    date = datetime.now(pytz.timezone('Europe/Berlin')) - timedelta(days=days_to_subtract)
    url = url + date.strftime("%Y-%m-%d")
    return url
