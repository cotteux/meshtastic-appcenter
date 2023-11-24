import re

from plugins.base_plugin import BasePlugin
from plugin_loader import load_plugins
from log_utils import get_logger
from meshtastic_utils import (
    connect_meshtastic,
    on_meshtastic_message,
    on_lost_meshtastic_connection,
    logger as meshtastic_logger,
)

class Plugin(BasePlugin):
    plugin_name = "help"

    @property
    def description(self):
        return f"List supported relay commands"

    def get_mesh_commands(self):
        return [self.plugin_name]

    async def handle_room_message(self, room, event, full_message):
        return False

    async def handle_meshtastic_message(self, packet, formatted_message, longname, meshnet_name):
        if (
            "decoded" in packet
            and "portnum" in packet["decoded"]
            and packet["decoded"]["portnum"] == "TEXT_MESSAGE_APP"
            and "text" in packet["decoded"]
        ):
            message = packet["decoded"]["text"]
            # message = message.strip()
            meshtastic_logger.info(f"msg - {message}")
            if f"!{self.plugin_name}" not in message:
               meshtastic_logger.info(f"pas bon plugins")
               return
        else : return 
	
        commands = []
        plugins = load_plugins()
        meshtastic_logger.info(f"voila - {plugins}")
        for plugin in plugins:
            commands.extend(plugin.get_mesh_commands())
            meshtastic_logger.info(f"v - {commands}")
        reply = "commandes: "+" , ".join(commands)
        from meshtastic_utils import connect_meshtastic

        meshtastic_client = connect_meshtastic()
        meshtastic_client.sendText(text=reply, destinationId=packet["fromId"])
        return True
