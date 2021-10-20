import os


def remove_words_from_string(query, stopwords, separator=" "):
    querywords = query.split(separator)

    resultwords = [word for word in querywords if word.lower() not in stopwords]
    return separator.join(resultwords)

def isDevStage():
    if os.environ.get('STAGE'):
        return os.environ['STAGE'] == 'dev'
    else:
        return False