import os
import re

def remove_words_from_string(value, stopwords, replace=""):
    replaced_value = value
    for word in stopwords:
        replaced_value = replaced_value.replace(word, replace)

    replaced_value = re.sub("\s\s+", " ", replaced_value)

    return replaced_value

def isDevStage():
    if os.environ.get('STAGE'):
        return os.environ['STAGE'] == 'dev'
    else:
        return False