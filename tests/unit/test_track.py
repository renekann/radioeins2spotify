import json
import os
import unittest
from unittest import TestCase, mock

from models.track import Track
from services.tracks_service import filter_for_new_tracks

@mock.patch.dict(os.environ, {"BUCKET_NAME": "bucket"})
class TestTrack(TestCase):
    def setUp(self) -> None:
        pass

    def load_json_file(self, filename):
        with open(f"./resources/{filename}", 'r') as outfile:
            return json.load(outfile)

    def test_load_forms(self) -> None:
        track1 = Track(123456789, "Foo Fighters & The Joy's Dinges?", "This is not the end (Radio Edit) feat. This & That")
        track2 = Track(12, "Eels", "Mr. E's Beautiful Blues")

        self.assertEqual(track1.searchString(), 'track:This is not the end This That artist:Foo Fighters The Joys Dinges')
        self.assertEqual(track2.searchString(), 'track:Mr Es Beautiful Blues artist:Eels')

    def test_track_filtering(self):
        old_tracks = [Track(**d) for d in self.load_json_file('pulled_tracks.json')]
        new_tracks = [Track(**d) for d in self.load_json_file('new_pulled_tracks.json')]

        set_difference = filter_for_new_tracks(new_tracks, old_tracks)

        self.assertIs(len(set_difference), 2)

    def test_older_tracks_filtering(self):
        old_tracks = [Track(**d) for d in self.load_json_file('pulled_older_tracks.json')]
        new_tracks = [Track(**d) for d in self.load_json_file('new_pulled_older_tracks.json')]

        set_difference = filter_for_new_tracks(new_tracks, old_tracks)

        self.assertIs(len(set_difference), 2)



if __name__ == '__main__':
    unittest.main()
