"""
This script connects a Meshtastic mesh network with an app system.
"""
import asyncio
from pubsub import pub
from typing import List
from db_utils import initialize_database, update_longnames, update_shortnames
from plugin_loader import load_plugins
from config import relay_config
from log_utils import get_logger
from meshtastic_utils import (
    connect_meshtastic,
    on_meshtastic_message,
    on_lost_meshtastic_connection,
    logger as meshtastic_logger,
)

logger = get_logger(name="Mestastic Apps")
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

    # Start the Matrix client
    while True:
        try:
            # Update longnames & shortnames
            update_longnames(meshtastic_interface.nodes)
            update_shortnames(meshtastic_interface.nodes)

            #matrix_logger.info("Syncing with server...")
            #await matrix_client.sync_forever(timeout=30000)
            #matrix_logger.info("Sync completed.")
        except Exception as e:
            meshtastic_logger.info(f"Error syncing with server: {e}")

        await asyncio.sleep(60)  # Update longnames & shortnames every 60 seconds


asyncio.run(main())
