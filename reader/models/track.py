import json
from hashlib import sha1
from utils.utils import remove_words_from_string

class Track:
    newTrack = False

    def __init__(self,
                 playtime,
                 artist,
                 title,
                 hash = None,
                 spotifyId = None):
        self.playtime = playtime
        self.artist = artist
        self.title = title

        if hash is None:
            self.hash = sha1(str(f"{artist}-{title}").encode('utf-8')).hexdigest()
        else:
            self.hash = hash

        if spotifyId is None:
            self.spotifyId = ""
        else:
            self.spotifyId = spotifyId

    def toJson(self):
        return json.dumps({"artist": self.artist, "title": self.title, "playtime": self.playtime, "hash": self.hash,
                           "spotifyId": self.spotifyId})
    def __repr__(self):
        return f"Artist: {self.artist} - {self.title} (playtime: {self.playtime}, spotifyId: {self.spotifyId}, hash: {self.hash})"

    def searchString(self):
        cleanupWords = [" x ",
                        "feat.",
                        "feat",
                        "Ft.",
                        "&",
                        "'",
                        "Edit",
                        "Radio",
                        "Single",
                        "Radio Edit",
                        "Radio-Edit",
                        "Radioedit",
                        "Live",
                        "(",
                        ")",
                        "?",
                        "!",
                        " - ",
                        " -",
                        "&",
                        "Konzertmitschnitt",
                        "Popsplits"]

        cleanedTitle = remove_words_from_string(self.title, cleanupWords).strip()
        cleanedArtist = remove_words_from_string(self.artist, cleanupWords).strip()

        return "track:" + cleanedTitle + " artist:" + cleanedArtist
