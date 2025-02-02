
import asyncio
import time
import meshtastic.tcp_interface
import meshtastic.serial_interface
from typing import List

from config import relay_config
from log_utils import get_logger
from db_utils import get_longname, get_shortname
from plugin_loader import load_plugins


logger = get_logger(name="Meshtastic")


meshtastic_client = None


def connect_meshtastic():
    global meshtastic_client
    if meshtastic_client:
        return meshtastic_client
    # Initialize Meshtastic interface
    connection_type = relay_config["meshtastic"]["connection_type"]
    retry_limit = (
        relay_config["meshtastic"]["retry_limit"]
        if "retry_limit" in relay_config["meshtastic"]
        else 3
    )
    attempts = 1
    successful = False
    if connection_type == "serial":
        serial_port = relay_config["meshtastic"]["serial_port"]
        logger.info(f"Connecting to serial port {serial_port} ...")
        while not successful and attempts <= retry_limit:
            try:
                meshtastic_client = meshtastic.serial_interface.SerialInterface(
                    serial_port
                )
                successful = True
            except Exception as e:
                attempts += 1
                if attempts <= retry_limit:
                    logger.warn(
                        f"Attempt #{attempts-1} failed. Retrying in {attempts} secs {e}"
                    )
                    time.sleep(attempts)
                else:
                    logger.error(f"Could not connect: {e}")
                    return None
    else:
        target_host = relay_config["meshtastic"]["host"]
        logger.info(f"Connecting to host {target_host} ...")
        while not successful and attempts <= retry_limit:
            try:
                meshtastic_client = meshtastic.tcp_interface.TCPInterface(
                    hostname=target_host
                )
                successful = True
            except Exception as e:
                attempts += 1
                if attempts <= retry_limit:
                    logger.warn(
                        f"Attempt #{attempts-1} failed. Retrying in {attempts} secs... {e}"
                    )
                    time.sleep(attempts)
                else:
                    logger.error(f"Could not connect: {e}")
                    return None

    nodeInfo = meshtastic_client.getMyNodeInfo()
    logger.info(
        f"Connected to {nodeInfo['user']['shortName']} / {nodeInfo['user']['hwModel']}"
    )
    return meshtastic_client


def on_lost_meshtastic_connection(interface):
    logger.error("Lost connection. Reconnecting...")
    connect_meshtastic()


# Callback for new messages from Meshtastic
def on_meshtastic_message(packet, loop=None):
    process = 0
    sender = packet["fromId"]
    receiver = packet["toId"]
    if sender == "" : 
        logger.debug(f"- VIDE ------------------")
        return

    if "text" in packet["decoded"] and packet["decoded"]["text"]:
        text = packet["decoded"]["text"]
        logger.debug(f"- {packet}")
        logger.debug(f"s: {sender}  d: {receiver}")

        if not receiver ==  '!fa666c80' :
            #logger.debug(f"{packet['channel']}")
            logger.debug(f"-non-")
            #channel = packet["channel"]
            process = 0
        else:
            if packet["decoded"]["portnum"] == "TEXT_MESSAGE_APP" and not receiver == '^all' :
               logger.debug(f"-oui-")
               process = 1
            else:
                logger.debug(f"Unknown packet")
                return

        logger.info(
            f"Processing inbound radio message from {sender}"
        )

        longname = get_longname(sender) or sender
        shortname = get_shortname(sender) or sender
        meshnet_name = relay_config["meshtastic"]["meshnet_name"]

        formatted_message = f"[{longname}/{meshnet_name}]: {text}"

        # Plugin functionality
        plugins = load_plugins()

        found_matching_plugin = False
        for plugin in plugins:
            if not found_matching_plugin :
                result = asyncio.run_coroutine_threadsafe(
                    plugin.handle_meshtastic_message(
                        packet, formatted_message, longname, meshnet_name
                    ),
                    loop=loop,
                )
                found_matching_plugin = result.result()
                if found_matching_plugin :
                    logger.debug(f"Processed by plugin {plugin.plugin_name}")

        if found_matching_plugin and process == 1:
            return

        #logger.info(
            #f"Relaying Meshtastic message from {longname} to Matrix: {formatted_message}"
        #)

    else:
        portnum = packet["decoded"]["portnum"]
        plugin = ""
        plugins = load_plugins()
        found_matching_plugin = False
        for plugin in plugins:
            if not found_matching_plugin:
                result = asyncio.run_coroutine_threadsafe(
                    plugin.handle_meshtastic_message(
                        packet, formatted_message=None, longname=None, meshnet_name=None
                    ),
                    loop=loop,
                )
                #logger.info(f"result =  {result.result()}"),
                found_matching_plugin = result.result()
                #logger.debug(f"pas le droit: {plugin.plugin_name}")
                if found_matching_plugin:
                    logger.debug(
                        f"Processed {portnum} with plugin {plugin.plugin_name}"
                    )
