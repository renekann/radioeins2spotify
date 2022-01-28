import json
import os
import unittest
from unittest import TestCase, mock

from helper.bucket_client import store, load
from models.track import Track


@mock.patch.dict(os.environ, {"BUCKET_NAME": "bucket"})
class TestBucketClient(TestCase):
    def setUp(self) -> None:
        pass

    def load_json_file(self, filename):
        with open(f"./resources/{filename}", 'r') as outfile:
            return json.load(outfile)

    def test_store_file(self) -> None:
        tracks = [Track(**d) for d in self.load_json_file('pulled_tracks.json')]
        json_string = json.dumps(tracks, default=lambda x: x.__dict__)
        store(data=json_string, key="tracks.json")

    def test_load_file(self) -> None:
        result = json.loads(load(key="tracks.json"))
        tracks = [Track(**d) for d in result]
        self.assertTrue(len(tracks) > 0)


if __name__ == '__main__':
    unittest.main()
