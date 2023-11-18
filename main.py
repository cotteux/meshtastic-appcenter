"""
This script connects a Meshtastic mesh network to 
It uses Meshtastic-python and App server respectively.
"""
import asyncio
from nio import (
    RoomMessageText,
    RoomMessageNotice,
)
from pubsub import pub
from typing import List
from db_utils import initialize_database, update_longnames, update_shortnames

)
from plugin_loader import load_plugins
from config import relay_config
from log_utils import get_logger
from meshtastic_utils import (
    connect_meshtastic,
    on_meshtastic_message,
    on_lost_meshtastic_connection,
    logger as meshtastic_logger,
)

logger = get_logger(name="M<>M Relay")
meshtastic_interface = connect_meshtastic()

async def main():
    # Initialize the SQLite database
    initialize_database()

    # Load plugins early
    load_plugins()

    # Register the Meshtastic message callback
    meshtastic_logger.info(f"Listening for inbound radio messages ...")
    pub.subscribe(
        on_meshtastic_message, "meshtastic.receive", loop=asyncio.get_event_loop()
    )
    pub.subscribe(
        on_lost_meshtastic_connection,
        "meshtastic.connection.lost",
    )
  
   asyncio.run(main())
