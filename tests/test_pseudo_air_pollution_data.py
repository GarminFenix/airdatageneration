"""
Unit tests for core functionality in air_data_generation.py that do not require numpy.
"""
import sys
import types

# Patch numpy (Generated using AI)
sys.modules['numpy'] = types.SimpleNamespace(interp=lambda *args, **kwargs: 0)

# Patch apscheduler with a dummy scheduler class (Generated using AI)
class DummyScheduler:
    def add_job(self, *args, **kwargs):
        pass
    def start(self):
        pass

background_mock = types.SimpleNamespace(BackgroundScheduler=lambda: DummyScheduler())
sys.modules['apscheduler.schedulers.background'] = background_mock
sys.modules['apscheduler'] = types.SimpleNamespace()
sys.modules['apscheduler.schedulers'] = types.SimpleNamespace(background=background_mock)

# Patch subscriptions_utils (Generated using AI)
sys.modules['subscriptions_utils'] = types.SimpleNamespace(notify_subscribers=lambda *args, **kwargs: None)


import unittest
from unittest.mock import patch, mock_open
from datetime import datetime, timezone
import json

from src.pseudo_air_pollution_data import load_json, PollutionData


class TestLoadJson(unittest.TestCase):
    """
    Unit tests for the load_json function.
    """

    def setUp(self):
        """
        Prepare mock JSON input for testing.
        """
        self.mock_json = json.dumps([
            {
                "systemCodeNumber": "SITE001",
                "dynamics": [
                    {
                        "co": "0.4",
                        "no": "0.1",
                        "no2": "0.2",
                        "rh": "45",
                        "temperature": "22.5",
                        "noise": "30.0",
                        "battery": "3.7",
                        "lastUpdated": "2025-05-19T00:00:00.000000+0000"
                    }
                ]
            }
        ])

    @patch("builtins.open", new_callable=mock_open, read_data="")
    @patch("json.load")
    def test_load_json_success(self, mock_json_load, mock_file):
        """
        Test that load_json correctly parses valid input and converts types.
        """
        mock_json_load.return_value = json.loads(self.mock_json)
        output = []
        result = load_json("dummy_path.json", output)
        self.assertTrue(result)
        self.assertEqual(len(output), 1)
        self.assertEqual(output[0]["systemCodeNumber"], "SITE001")
        self.assertEqual(len(output[0]["dynamics"]), 1)
        self.assertIsInstance(output[0]["dynamics"][0]["co"], float)
        self.assertIsInstance(output[0]["dynamics"][0]["rh"], int)
        self.assertIsInstance(output[0]["dynamics"][0]["lastUpdated"], datetime)


class TestPollutionData(unittest.TestCase):
    """
    Unit tests for the PollutionData class excluding interpolation logic.
    """

    def setUp(self):
        """
        Set up a PollutionData instance with mock data.
        """
        self.pollution_data = PollutionData()
        self.pollution_data.data = [
            {
                "systemCodeNumber": "SITE001",
                "dynamics": [
                    {
                        "co": 0.4,
                        "no": 0.1,
                        "no2": 0.2,
                        "rh": 45,
                        "temperature": 22.5,
                        "noise": 30.0,
                        "battery": 3.7,
                        "lastUpdated": datetime(2025, 5, 19, 0, 0, 0, tzinfo=timezone.utc)
                    }
                ]
            }
        ]
        self.pollution_data.site_metadata_cache = {
            "SITE001": {"lat": 59.91, "lon": 10.75}
        }
        self.pollution_data._PollutionData__loaded = True

    def test_get_pollution_data_valid(self):
        """
        Test that pollution data is retrieved correctly for a valid timestamp and site.
        """
        timestamp = datetime(2025, 5, 19, 0, 0, 0, tzinfo=timezone.utc)
        result = self.pollution_data.get_pollution_data(timestamp, "SITE001")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["co"], 0.4)

    def test_get_pollution_data_invalid_timestamp(self):
        """
        Test that an invalid timestamp string returns None.
        """
        result = self.pollution_data.get_pollution_data("invalid", "SITE001")
        self.assertIsNone(result)

    def test_get_site_coordinates(self):
        """
        Test that coordinates are returned for a known site.
        """
        coords = self.pollution_data.get_site_coordinates("SITE001")
        self.assertEqual(coords, {"lat": 59.91, "lon": 10.75})

    def test_get_all_sites_coordinates(self):
        """
        Test that all site coordinates are returned as a list of dictionaries.
        """
        all_coords = self.pollution_data.get_all_sites_coordinates()
        self.assertEqual(len(all_coords), 1)
        self.assertEqual(all_coords[0]["systemCodeNumber"], "SITE001")
        self.assertEqual(all_coords[0]["lat"], 59.91)
        self.assertEqual(all_coords[0]["lon"], 10.75)


if __name__ == "__main__":
    unittest.main()