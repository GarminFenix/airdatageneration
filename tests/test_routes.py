"""
Unit tests for pollution data Flask endpoints.
"""
import sys
import os

# Add src/ to sys.path so we can import routes.py as a top-level module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from routes import pollution_bp 
import unittest
from unittest.mock import patch
from flask import Flask


class TestPollutionRoutes(unittest.TestCase):
    """
    Test suite for pollution data API endpoints.
    """

    def setUp(self):
        """
        Set up Flask test client.
        """
        app = Flask(__name__)
        app.register_blueprint(pollution_bp)
        self.client = app.test_client()

    @patch("routes.simulate_live_data")
    def test_subscribe_success(self, mock_simulate):
        """
        Test successful subscription request.
        """
        payload = {
            "notificationUrl": "http://example.com",
            "subscriptions": ["AIR QUALITY DYNAMIC"]
        }
        response = self.client.post("/pollutiondata/subscribe", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn("SubscriptinID", response.get_json())

    def test_subscribe_missing_fields(self):
        """
        Test subscription request with missing fields.
        """
        response = self.client.post("/pollutiondata/subscribe", json={})
        self.assertEqual(response.status_code, 400)

    def test_get_simtime(self):
        """
        Test retrieval of current simulation time.
        """
        response = self.client.get("/pollutiondata/simtime")
        self.assertEqual(response.status_code, 200)
        self.assertIn("current_simulation_time", response.get_json())

    def test_set_simtime_valid(self):
        """
        Test setting simulation time with valid input.
        """
        payload = {"timestamp": "2025-05-19T18:30:00+00:00"}
        response = self.client.post("/pollutiondata/simtime", json=payload)
        self.assertEqual(response.status_code, 200)

    def test_set_simtime_invalid(self):
        """
        Test setting simulation time with invalid input.
        """
        payload = {"timestamp": "invalid"}
        response = self.client.post("/pollutiondata/simtime", json=payload)
        self.assertEqual(response.status_code, 400)

    @patch("routes.pollution_data.get_pollution_data")
    @patch("routes.pollution_data.get_site_coordinates")
    def test_requested_pollution_data_success(self, mock_coords, mock_data):
        """
        Test successful retrieval of pollution data.
        """
        mock_coords.return_value = {"lat": 59.91, "lon": 10.75}
        mock_data.return_value = [{"co": 0.4, "lastUpdated": "2025-05-19T00:00:00.000+0000"}]

        response = self.client.get("/pollutiondata/?timestamp=2025-05-19T00:00:00.000+0000&site=SITE001")
        self.assertEqual(response.status_code, 200)
        self.assertIn("coordinates", response.get_json())

    @patch("routes.pollution_data.get_all_sites_coordinates")
    def test_get_all_coordinates_success(self, mock_all_coords):
        """
        Test retrieval of all site metadata.
        """
        mock_all_coords.return_value = [{"systemCodeNumber": "SITE001", "lat": 59.91, "lon": 10.75}]
        response = self.client.get("/pollutiondata/sitemetadata")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)


if __name__ == "__main__":
    unittest.main()