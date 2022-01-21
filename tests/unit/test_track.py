import os
import unittest
from unittest import TestCase

from models.track import Track


class TestTrack(TestCase):
    def setUp(self) -> None:
        pass

    def test_load_forms(self) -> None:
        track = Track(123456789, "Foo Fighters & The Joy's Dinges?", "This is not the end (Radio Edit) feat. This & That")

        search_string = track.searchString()

        assert(search_string, 'track:This is not the end This That artist:Foo Fighters The Joys Dinges')


if __name__ == '__main__':
    unittest.main()
