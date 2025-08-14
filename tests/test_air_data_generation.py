"""
Integration tests for the pollution data generator.

These tests validate the structure and content of the generated JSON file
without modifying the original production code. They ensure:
- Correct number of sites
- Proper timestamp intervals
- Expected value ranges based on busy/quiet periods
"""

import unittest
import json
from datetime import datetime, timedelta
import os
from src.air_data_generation import is_busy_period  

class TestPollutionDataOutput(unittest.TestCase):
    """
    Test suite for validating the generated pollution_data.json file.
    """

    @classmethod
    def setUpClass(cls):
        """
        Load the JSON data once for all tests.
        """
        cls.file_path = os.path.join("data", "pollution_data.json")
        with open(cls.file_path, "r") as f:
            cls.data = json.load(f)

    def test_number_of_sites(self):
        """
        Test that the dataset contains exactly 130 sites.
        """
        self.assertEqual(len(self.data), 130)

    def test_site_structure(self):
        """
        Test that each site has a systemCodeNumber and a dynamics list.
        """
        for site in self.data:
            self.assertIn("systemCodeNumber", site)
            self.assertIn("dynamics", site)
            self.assertIsInstance(site["dynamics"], list)

    def test_dynamics_entry_structure(self):
        """
        Test that each dynamics entry contains all expected keys.
        """
        expected_keys = {
            "co", "no", "no2", "rh", "temperature", "noise", "battery", "lastUpdated"
        }
        for site in self.data:
            for entry in site["dynamics"]:
                self.assertTrue(expected_keys.issubset(entry.keys()))

    def test_timestamp_interval_consistency(self):
        """
        Test that timestamps for each site are spaced exactly 10 minutes apart.
        """
        for site in self.data:
            timestamps = [
                datetime.strptime(entry["lastUpdated"], "%Y-%m-%dT%H:%M:%S.000+0000")
                for entry in site["dynamics"]
            ]
            for i in range(1, len(timestamps)):
                delta = timestamps[i] - timestamps[i - 1]
                self.assertEqual(delta, timedelta(minutes=10))

    def test_value_ranges_based_on_period(self):
        """
        Test that pollutant and noise values fall within expected ranges
        depending on whether the timestamp is during a busy period.
        """
        for site in self.data:
            for entry in site["dynamics"]:
                ts = datetime.strptime(entry["lastUpdated"], "%Y-%m-%dT%H:%M:%S.000+0000")
                busy = is_busy_period(ts)

                # CO
                co = entry["co"]
                self.assertTrue(0.5 <= co <= 5.0 if busy else 0.1 <= co <= 0.17)

                # NO
                no = entry["no"]
                self.assertTrue(20 <= no <= 150 if busy else 1 <= no <= 10)

                # NO2
                no2 = entry["no2"]
                self.assertTrue(40 <= no2 <= 300 if busy else 5 <= no2 <= 30)

                # Noise
                noise = entry["noise"]
                self.assertTrue(70 <= noise <= 100 if busy else 30 <= noise <= 60)

                # RH
                rh = entry["rh"]
                if busy:
                    self.assertTrue(70 <= rh <= 85)
                else:
                    self.assertTrue(55 <= rh <= 60)

    def test_battery_range(self):
        """
        Test that battery values are always between 3.5 and 4.2 volts.
        """
        for site in self.data:
            for entry in site["dynamics"]:
                battery = entry["battery"]
                self.assertTrue(3.5 <= battery <= 4.2)

    def test_temperature_ranges_by_hour(self):
        """
        Test that temperature values fall within expected ranges based on hour.
        """
        for site in self.data:
            for entry in site["dynamics"]:
                ts = datetime.strptime(entry["lastUpdated"], "%Y-%m-%dT%H:%M:%S.000+0000")
                hour = ts.hour
                temp = entry["temperature"]

                if 10 <= hour < 18:
                    self.assertTrue(18 <= temp <= 24)
                elif 22 <= hour or hour < 6:
                    self.assertTrue(5 <= temp <= 10)
                else:
                    self.assertTrue(7 <= temp <= 17)


if __name__ == '__main__':
    unittest.main()