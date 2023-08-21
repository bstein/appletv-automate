import asyncio
import inquirer
from pyatv import connect, interface
import sys

from pair_apple_tvs import pair_apple_tv
from utils import CREDENTIALS_LAST_CONNECTED_KEY, get_apple_tvs, get_credentials, get_device_summary_str, get_inquirer_padding, get_log_prefix, protocol_str_to_protocol, read_credentials_json, save_last_connected


async def connect_apple_tv() -> interface.AppleTV:
    """Scan for Apple TVs on network, ask which one to connect to, pair if needed, establish connection, and return connected_apple_tv.

    NOTE: connected_apple_tv.close() must be called when finished"""
    loop = asyncio.get_event_loop()
    apple_tvs = await get_apple_tvs()

    credentials = read_credentials_json()
    mac_adrs_with_credentials = [
        mac_adr for mac_adr in credentials.keys() if not mac_adr.startswith('_')]

    apple_tvs_mac_adrs = [''] * len(apple_tvs)
    apple_tvs_is_paired = [False] * len(apple_tvs)
    device_connect_summary_strs = [''] * len(apple_tvs)
    for i in range(len(apple_tvs)):
        apple_tvs_mac_adrs[i] = apple_tvs[i].device_info.mac
        apple_tvs_is_paired[i] = apple_tvs_mac_adrs[i] in mac_adrs_with_credentials
        device_connect_summary_strs[i] = '{0:s}{1:s}'.format(
            get_device_summary_str(apple_tvs[i]),
            (' - paired' if apple_tvs_is_paired[i] else '')
        )

    # Determine the index of the device to connect to by default
    idx_to_connect = None
    if CREDENTIALS_LAST_CONNECTED_KEY in credentials \
            and credentials[CREDENTIALS_LAST_CONNECTED_KEY] \
            and credentials[CREDENTIALS_LAST_CONNECTED_KEY] in apple_tvs_mac_adrs:
        # Use index of the device that was last connected
        idx_to_connect = apple_tvs_mac_adrs.index(
            credentials[CREDENTIALS_LAST_CONNECTED_KEY])
    elif True in apple_tvs_is_paired:
        # Use index of the first device that has already been paired
        idx_to_connect = apple_tvs_is_paired.index(True)
    else:
        # Fallback to first device in list
        idx_to_connect = 0

    if len(apple_tvs) > 1:
        # Ask which Apple TV the user wants to connect to, since there is more than one on the network
        select_to_connect = inquirer.List(
            'select_to_connect',
            message='{0:s}Which Apple TV would you like to connect to?'.format(
                get_inquirer_padding()),
            choices=device_connect_summary_strs,
            default=device_connect_summary_strs[idx_to_connect]
        )
        answers = inquirer.prompt(
            [select_to_connect], raise_keyboard_interrupt=True)
        idx_to_connect = device_connect_summary_strs.index(
            answers['select_to_connect'])

    if not apple_tvs_is_paired[idx_to_connect]:
        # Selected Apple TV has not yet been paired, so pair it before attempting to connect
        await pair_apple_tv(apple_tvs[idx_to_connect], device_connect_summary_strs[idx_to_connect])
        return await connect_apple_tv()

    print(
        f'{get_log_prefix()}Connecting to {get_device_summary_str(apple_tvs[idx_to_connect])}...')
    # Set credentials for each protocol
    for protocol_str, credentials in get_credentials(apple_tvs_mac_adrs[idx_to_connect]).items():
        apple_tvs[idx_to_connect].set_credentials(
            protocol_str_to_protocol(protocol_str), credentials)

    connected_apple_tv = None
    try:
        connected_apple_tv = await connect(apple_tvs[idx_to_connect], loop)
        print(
            f'{get_log_prefix()}Successfully connected to {get_device_summary_str(apple_tvs[idx_to_connect])}!')
        save_last_connected(apple_tvs_mac_adrs[idx_to_connect])
    except:
        print(
            f'{get_log_prefix()}ERROR: Failed to connect to {get_device_summary_str(apple_tvs[idx_to_connect])}!', file=sys.stderr)
    finally:
        return connected_apple_tv
