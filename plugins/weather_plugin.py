import re
import requests

from plugins.base_plugin import BasePlugin
from datetime import datetime

class Plugin(BasePlugin):
    plugin_name = "meteo"

    @property
    def description(self):
        return f"Afficher les prévisions météo à Sherbrooke"

    def generate_forecast(self, latitude, longitude):
        url = f"https://api.open-meteo.com/v1/forecast?latitude=45.40&longitude=-71.89&hourly=temperature_2m,precipitation_probability,weathercode,cloudcover&timezone=America%2FNew_York&forecast_days=1&current_weather=true"
   #     url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,precipitation_probability,weathercode,cloudcover&forecast_days=1&current_weather=true&timezone=America%2FNew_York"

        try:
            response = requests.get(url)
            data = response.json()
            # Extract relevant weather data
            current_temp = data["current_weather"]["temperature"]
            current_weather_code = data["current_weather"]["weathercode"]
            is_day = data["current_weather"]["is_day"]
            currentDateAndTime = datetime.now()

           # forecast_2h_temp = data["hourly"]["temperature_2m"][currentDateAndTime.hour+1]
           # forecast_2h_precipitation = data["hourly"]["precipitation_probability"][currentDateAndTime.hour+1]
           # forecast_2h_weather_code = data["hourly"]["weathercode"][currentDateAndTime.hour+1]
           # forecast_5h_temp = data["hourly"]["temperature_2m"][currentDateAndTime.hour+4]
           # forecast_5h_precipitation = data["hourly"]["precipitation_probability"][currentDateAndTime.hour+4]
           # forecast_5h_weather_code = data["hourly"]["weathercode"][currentDateAndTime.hour+4]

            def weather_code_to_text(weather_code, is_day):
                weather_mapping = {
                    0: "☀️ Ensoleillé" if is_day else "🌙 Dégagé",
                    1: "⛅️ Passages Nuageux" if is_day else "🌙⛅️ Dégagé",
                    2: "🌤️ Généralement Dégagé" if is_day else "🌙🌤️ Généralement Dégagé",
                    3: "🌥️ Nuageux avec éclaircies" if is_day else "🌙🌥️ Généralement Dégagé",
                    4: "☁️ Nuageux" if is_day else "🌙☁️ Nuageux",
                    5: "🌧️ Averse" if is_day else "🌙🌧️ Averses",
                    6: "⛈️ Orage" if is_day else "🌙⛈️ Orage",
                    7: "❄️ Neige" if is_day else "🌙❄️ Neige",
                    8: "🌧️❄️ Mélange Hivernal" if is_day else "🌙🌧️❄️ Mélange Hivernal",
                    9: "🌫️ Brouillard" if is_day else "🌙🌫️ Brouillard",
                    10: "💨 Venteux" if is_day else "🌙💨 Venteux",
                    11: "🌧️☈️ orage/grêle" if is_day else "🌙🌧️☈️ orage/grêle",
                    12: "🌫️ Brouillard" if is_day else "🌙🌫️ Brouillard",
                    13: "🌫️ Brouillard" if is_day else "🌙🌫️ Brouillard",
                    14: "🌫️ Brouillard" if is_day else "🌙🌫️ Brouillard",
                    15: "🌋 Volcan" if is_day else "🌙🌋 Volcan",
                    16: "🌧️ Pluvieux" if is_day else "🌙🌧️ Pluvieux",
                    17: "🌫️ Brouillard" if is_day else "🌙🌫️ Brouillard",
                    18: "🌪️ Tornade" if is_day else "🌙🌪️ Tornade",
                }

                return weather_mapping.get(weather_code, "❓ Unknown")

            # Generate one-line weather forecast
            forecast = f"Météo à Sherbrooke | {weather_code_to_text(current_weather_code, is_day)} : {current_temp}°C "
          #  forecast += f"| +2H : {weather_code_to_text(forecast_2h_weather_code, is_day)} : {forecast_2h_temp}°C {forecast_2h_precipitation}% "
          #  forecast += f"| +5H : {weather_code_to_text(forecast_5h_weather_code, is_day)} : {forecast_5h_temp}°C {forecast_5h_precipitation}%"

            return forecast

        except requests.exceptions.RequestException as e:
            print(f"Erreur: {e}")
            return None

    async def handle_meshtastic_message(
        self, packet, formatted_message, longname, meshnet_name
    ):
        if (
            "decoded" in packet
            and "portnum" in packet["decoded"]
            and packet["decoded"]["portnum"] == "TEXT_MESSAGE_APP"
            and "text" in packet["decoded"]
        ):
            message = packet["decoded"]["text"]
            message = message.strip()

            if f"!{self.plugin_name}" not in message:
                return False

            from meshtastic_utils import connect_meshtastic

            meshtastic_client = connect_meshtastic()
            if packet["fromId"] in meshtastic_client.nodes:
                weather_notice = "Cannot determine location"
                requesting_node = meshtastic_client.nodes.get(packet["fromId"])
                if (
                    requesting_node
                    and "position" in requesting_node
                    and "latitude" in requesting_node["position"]
                    and "longitude" in requesting_node["position"]
                ):
                    weather_notice = self.generate_forecast(
                        latitude=requesting_node["position"]["latitude"],
                        longitude=requesting_node["position"]["longitude"],
                    )

                meshtastic_client.sendText(
                    text=weather_notice,
                    destinationId=packet["fromId"],
                )
            return True

    def get_matrix_commands(self):
        return []

    def get_mesh_commands(self):
        return [self.plugin_name]

    async def handle_room_message(self, room, event, full_message):
        return False
