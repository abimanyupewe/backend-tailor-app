import json
import math
from channels.generic.websocket import AsyncWebsocketConsumer

class DistanceCalculatorConsumer(AsyncWebsocketConsumer):
    """
    WebSocket Consumer for real-time distance calculation between User and Tailors/Locations.
    """
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            "status": "connected",
            "message": "WebSocket connection established for distance calculation."
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get("action")

            if action == "calculate_distance":
                origin_lat = float(data.get("origin_lat"))
                origin_lon = float(data.get("origin_lon"))
                dest_lat = float(data.get("dest_lat"))
                dest_lon = float(data.get("dest_lon"))

                distance_km = self.haversine(origin_lat, origin_lon, dest_lat, dest_lon)

                await self.send(text_data=json.dumps({
                    "action": "distance_result",
                    "distance_km": round(distance_km, 2),
                    "distance_meters": round(distance_km * 1000, 1),
                    "unit": "km"
                }))
            else:
                await self.send(text_data=json.dumps({"error": "Invalid action"}))

        except (ValueError, TypeError) as e:
            await self.send(text_data=json.dumps({"error": f"Invalid payload parameters: {str(e)}"}))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON format"}))

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance between two points on the earth in kilometers.
        """
        R = 6371.0  # Radius of Earth in kilometers
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)

        a = (math.sin(d_lat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(d_lon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
