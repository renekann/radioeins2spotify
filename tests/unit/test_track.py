import os
import unittest
from unittest import TestCase

from models.track import Track


class TestTrack(TestCase):
    def setUp(self) -> None:
        pass

    def test_load_forms(self) -> None:
        track1 = Track(123456789, "Foo Fighters & The Joy's Dinges?", "This is not the end (Radio Edit) feat. This & That")
        track2 = Track(12, "Eels", "Mr. E's Beautiful Blues")

        self.assertEqual(track1.searchString(), 'track:This is not the end This That artist:Foo Fighters The Joys Dinges')
        self.assertEqual(track2.searchString(), 'track:Mr Es Beautiful Blues artist:Eels')


if __name__ == '__main__':
    unittest.main()
