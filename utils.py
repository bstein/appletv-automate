import aiohttp
import asyncio
from datetime import datetime
import json
from os import path
from pyatv import scan, const, convert, interface
import sys

import config


# The filename of the credentials JSON file, relative to the root path
#   WARNING - if you change this, be sure to add the new filename to .gitignore to avoid committing your credentials!
CREDENTIALS_FILE_NAME: str = 'credentials.json'

# The credentials JSON file key to store the last connected device MAC address
CREDENTIALS_LAST_CONNECTED_KEY = '_last_connected'


def get_log_prefix(include_time: bool = True, class_name: str = ""):
    """Return log prefix string, plus 1 * ' ' for padding

    When include_time = True, return an ISO 8601 timestamp for the current time

    When include_time = False, return an equal-length padded string
    """
    # isoformat() returns a str like 'YYYY-MM-DD HH:MM:SS', which has length of 19 characters
    timestamp = datetime.now().replace(
        microsecond=0).isoformat() if include_time else ' ' * 19
    class_name_prefix = ' {0:s}:'.format(class_name) if class_name else ''
    return '{0:s}{1:s} '.format(timestamp, class_name_prefix)


def get_inquirer_padding():
    """Return prefix padding string, for use before indented inquirer questions"""
    # Slice the padded string characters after the first 4, since inquirer adds a prefix like '[?] '
    return get_log_prefix(False)[4:]


def s_if_plural(length: int):
    """Return empty string if length == 1, else return "s" """
    return '' if length == 1 else 's'


def is_apple_tv(device: interface.BaseConfig):
    """Return whether the provided device operating_system is tvOS"""
    return device.device_info.operating_system == const.OperatingSystem.TvOS


async def get_apple_tvs():
    """Scan for devices on network and returns a list of Apple TVs.

    If there are none, print an error message and call exit(1).
    """
    loop = asyncio.get_event_loop()

    print(f'{get_log_prefix()}Discovering devices on network...')
    devices = await scan(loop, timeout=config.SCAN_TIMEOUT_SECONDS)
    apple_tvs = [device for device in devices if is_apple_tv(device)]

    print(f'{get_log_prefix()}Found {len(devices)} device{s_if_plural(len(devices))}, including {len(apple_tvs)} Apple TV{s_if_plural(len(apple_tvs))}, on network')

    if len(apple_tvs) == 0:
        print(f'{get_log_prefix()}ERROR: No Apple TVs were found!', file=sys.stderr)
        exit(1)

    return apple_tvs


def get_device_summary_str(device: interface.BaseConfig):
    """Return formatted summary string containing key details about the provided device"""
    return '{0:s} ({1:s})'.format(device.name, device.device_info.mac)


def service_to_protocol_str(service: interface.BaseService):
    """Convert provided service's pyatv internal API protocol to string"""
    return convert.protocol_str(service.protocol)


def protocol_str_to_protocol(protocol_str: str):
    """Convert string to pyatv internal API protocol"""
    return {
        'MRP': const.Protocol.MRP,
        'DMAP': const.Protocol.DMAP,
        'AirPlay': const.Protocol.AirPlay,
        'Companion': const.Protocol.Companion,
        'RAOP': const.Protocol.RAOP,
    }.get(protocol_str, protocol_str)


def read_credentials_json() -> dict:
    """Read and return contents of credentials JSON file or {}"""
    if path.exists(CREDENTIALS_FILE_NAME):
        with open(CREDENTIALS_FILE_NAME, 'r') as openfile:
            try:
                credentials = json.load(openfile)
                if credentials:
                    return credentials
            except:
                pass

    return {}


def write_credentials_json(credentials_json: dict):
    """Write to credentials JSON file, overwriting any existing contents"""
    json_object = json.dumps(credentials_json, indent=2)
    with open(CREDENTIALS_FILE_NAME, 'w') as outfile:
        outfile.write(json_object)


def get_credentials(device_mac: str):
    """Return credentials for provided device_mac in credentials JSON file or None if not saved"""
    credentials = read_credentials_json()
    return credentials[device_mac] if device_mac in credentials else None


def save_credential(device_mac: str, protocol: str, value: str):
    """Write new or updated credentials for provided device_mac to credentials JSON file"""
    credentials = read_credentials_json()

    # Add or update credentials[device_mac]
    cred_entry_for_device = credentials[device_mac] if device_mac in credentials else {
    }
    cred_entry_for_device[protocol] = value
    credentials[device_mac] = cred_entry_for_device

    write_credentials_json(credentials)


def save_last_connected(device_mac: str):
    """Write new or updated device_mac value to "_last_connected" entry to credentials JSON file"""
    credentials = read_credentials_json()
    credentials[CREDENTIALS_LAST_CONNECTED_KEY] = device_mac
    write_credentials_json(credentials)


async def publish_event_to_ifttt_webhooks(event_name: str):
    """Send POST request with the provided event_name to IFTTT for Webhooks integrations (see: https://ifttt.com/maker_webhooks)"""
    print(f'{get_log_prefix()}Sending POST request to IFTTT for event: "{event_name}"')

    if not config.IFTTT_API_KEY:
        print(f'{get_log_prefix(False)}WARNING: Skipping sending POST request to IFTTT because IFTTT_API_KEY was not specified in config.py!', file=sys.stderr)
        return

    request_url = 'https://maker.ifttt.com/trigger/{0:s}/with/key/{1:s}'.format(
        event_name, config.IFTTT_API_KEY)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(request_url) as response:
                print(
                    f'{get_log_prefix()}Received response from IFTTT with status code: {response.status}')
    except Exception as ex:
        print(f'{get_log_prefix()}ERROR: Failed when sending POST request to IFTTT! Details:\n{ex}', sys.stderr)
