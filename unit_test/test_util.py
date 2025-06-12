import unittest
from unittest.mock import MagicMock
import sys
import os
import src.util as util


class TestUtil(unittest.TestCase):
    def test_iso_duration_to_minutes(self):
        self.assertEqual(util.iso_duration_to_minutes('PT5M30S'), 5.5)
        self.assertEqual(util.iso_duration_to_minutes('PT10M'), 10.0)
        self.assertEqual(util.iso_duration_to_minutes('PT45S'), 0.75)
        self.assertEqual(util.iso_duration_to_minutes('PT0S'), 0.0)
        self.assertEqual(util.iso_duration_to_minutes('PT'), 0.0)
        self.assertEqual(util.iso_duration_to_minutes(''), 0.0)

    def test_minutes_to_hours(self):
        self.assertEqual(util.minutes_to_hours(130), "2h 10m")
        self.assertEqual(util.minutes_to_hours(60), "1h")
        self.assertEqual(util.minutes_to_hours(59), "59m")
        self.assertEqual(util.minutes_to_hours(0), "0m")

    def test_get_channel_id(self):
        service = MagicMock()
        service.channels().list().execute.return_value = {'items': [{'id': 'abc123'}]}
        self.assertEqual(util.get_channel_id(service, 'user'), 'abc123')

    def test_get_playlist_id_found(self):
        service = MagicMock()
        service.playlists().list().execute.return_value = {
            'items': [
                {'snippet': {'title': 'MyPlaylist'}, 'id': 'pl123'},
                {'snippet': {'title': 'Other'}, 'id': 'pl456'}
            ]
        }
        self.assertEqual(util.get_playlist_id(service, 'cid', 'MyPlaylist'), 'pl123')

    def test_get_playlist_id_not_found(self):
        service = MagicMock()
        service.playlists().list().execute.return_value = {
            'items': [{'snippet': {'title': 'Other'}, 'id': 'pl456'}]
        }
        with self.assertRaises(ValueError):
            util.get_playlist_id(service, 'cid', 'MissingPlaylist')

    def test_get_video_ids(self):
        service = MagicMock()
        # Simulate two pages of results
        service.playlistItems().list().execute.side_effect = [
            {'items': [{'contentDetails': {'videoId': 'v1'}}, {'contentDetails': {'videoId': 'v2'}}], 'nextPageToken': 'abc'},
            {'items': [{'contentDetails': {'videoId': 'v3'}}]}
        ]
        result = util.get_video_ids(service, 'plid', max_results=2)
        self.assertEqual(result, ['v1', 'v2', 'v3'])

    def test_get_video_durations(self):
        service = MagicMock()
        service.videos().list().execute.return_value = {
            'items': [
                {'contentDetails': {'duration': 'PT5M'}},
                {'contentDetails': {'duration': 'PT2M30S'}}
            ]
        }
        self.assertAlmostEqual(util.get_video_durations(service, ['v1', 'v2']), 7.5)

    def test_get_video_title(self):
        service = MagicMock()
        service.videos().list().execute.return_value = {
            'items': [
                {'snippet': {'title': 'Video 1'}},
                {'snippet': {'title': 'Video 2'}}
            ]
        }
        titles = util.get_video_title(service, ['v1', 'v2'])
        self.assertEqual(titles, ['Video 1', 'Video 2'])

    def test_get_video_title_empty(self):
        service = MagicMock()
        with self.assertRaises(ValueError):
            util.get_video_title(service, [])

if __name__ == '__main__':
    unittest.main()