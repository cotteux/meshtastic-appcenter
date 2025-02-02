import re
import statistics
from plugins.base_plugin import BasePlugin


class Plugin(BasePlugin):
    plugin_name = "health"

    @property
    def description(self):
        return "Show mesh health using avg battery, SNR, AirUtil"

    def generate_response(self):
        from meshtastic_utils import connect_meshtastic

        meshtastic_client = connect_meshtastic()
        battery_levels = []
        air_util_tx = []
        snr = []

        for node, info in meshtastic_client.nodes.items():
            if "deviceMetrics" in info:
                if "batteryLevel" in info["deviceMetrics"]:
                    battery_levels.append(info["deviceMetrics"]["batteryLevel"])
                if "airUtilTx" in info["deviceMetrics"]:
                    air_util_tx.append(info["deviceMetrics"]["airUtilTx"])
            if "snr" in info:
                snr.append(info["snr"])

        low_battery = len([n for n in battery_levels if n <= 10])
        radios = len(meshtastic_client.nodes)
        avg_battery = statistics.mean(battery_levels) if battery_levels else 0
        mdn_battery = statistics.median(battery_levels)
        avg_air = statistics.mean(air_util_tx) if air_util_tx else 0
        mdn_air = statistics.median(air_util_tx)
        avg_snr = statistics.mean(snr) if snr else 0
        mdn_snr = statistics.median(snr)

        return f"""Nodes: {radios}
Battery: {avg_battery:.1f}% / {mdn_battery:.1f}% (avg / median)
Nodes with Low Battery (< 10): {low_battery}
Air Util: {avg_air:.2f} / {mdn_air:.2f} (avg / median)
SNR: {avg_snr:.2f} / {mdn_snr:.2f} (avg / median)
"""

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
                return

            from meshtastic_utils import connect_meshtastic

            meshtastic_client = connect_meshtastic()
            response = self.generate_response()
            meshtastic_client.sendText(text=response, destinationId=packet["fromId"])
            return True


    async def handle_room_message(self, room, event, full_message):
        full_message = full_message.strip()
        if not self.matches(full_message):
            return False
        return True
