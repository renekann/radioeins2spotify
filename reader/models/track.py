import json
from hashlib import sha1
from helper.utils import remove_words_from_string


class Track:
    newTrack = False

    def __init__(self,
                 playtime,
                 artist,
                 title,
                 hash=None,
                 spotify_id=None):
        self.playtime = playtime
        self.artist = artist
        self.title = title

        if hash is None:
            self.hash = sha1(str(f"{artist}-{title}").encode('utf-8')).hexdigest()
        else:
            self.hash = hash

        if spotify_id is None:
            self.spotifyId = ""
        else:
            self.spotifyId = spotify_id

    def toJson(self):
        return json.dumps({"artist": self.artist, "title": self.title, "playtime": self.playtime, "hash": self.hash,
                           "spotifyId": self.spotifyId})

    def __repr__(self):
        return f"Artist: {self.artist} - {self.title} (playtime: {self.playtime}, spotifyId: {self.spotifyId}, hash: {self.hash})"

    def __hash__(self):
        return hash(self.hash)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.hash == other.hash

    def searchString(self):
        cleanup_words = [" x ",
                        "feat.",
                        "feat",
                        "Ft.",
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
                        ",",
                        " - ",
                        " -",
                        "&",
                        ".",
                        "Konzertmitschnitt",
                        "Popsplits"]

        cleaned_title = remove_words_from_string(self.title, cleanup_words).strip()
        cleaned_artist = remove_words_from_string(self.artist, cleanup_words).strip()

        return "track:" + cleaned_title + " artist:" + cleaned_artist
