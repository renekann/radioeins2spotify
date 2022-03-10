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

    @unittest.skip("Skip because s3 is not mocked here")
    def test_store_file(self, mock_s3_client) -> None:
        tracks = [Track(**d) for d in self.load_json_file('pulled_tracks.json')]
        json_string = json.dumps(tracks, default=lambda x: x.__dict__)
        store(data=json_string, key="tracks.json")

        self.assertTrue(mock_s3_client.return_value.list_buckets.call_count == 1)

    @unittest.skip("Skip because s3 is not mocked here")
    def test_load_file(self) -> None:
        result = json.loads(load(key="tracks.json"))
        tracks = [Track(**d) for d in result]
        self.assertTrue(len(tracks) > 0)


if __name__ == '__main__':
    unittest.main()
