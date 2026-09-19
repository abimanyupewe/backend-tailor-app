from django.test import TestCase
from channels.testing import WebsocketCommunicator
from tailor.consumers import DistanceCalculatorConsumer

class DistanceCalculatorConsumerTest(TestCase):
    async def test_distance_calculation(self):
        communicator = WebsocketCommunicator(DistanceCalculatorConsumer.as_asgi(), "/ws/distance/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Receive connection message
        response = await communicator.receive_json_from()
        self.assertEqual(response.get("status"), "connected")

        # Send calculate_distance action
        await communicator.send_json_to({
            "action": "calculate_distance",
            "origin_lat": -6.200000,
            "origin_lon": 106.816666,
            "dest_lat": -6.175392,
            "dest_lon": 106.827153
        })

        response = await communicator.receive_json_from()
        self.assertEqual(response.get("action"), "distance_result")
        self.assertIn("distance_km", response)
        self.assertIn("distance_meters", response)
        self.assertEqual(response.get("unit"), "km")

        await communicator.disconnect()
