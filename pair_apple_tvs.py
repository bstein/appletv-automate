
import asyncio
import inquirer
from pyatv import pair, interface
from random import randint
import re
import sys

from utils import get_apple_tvs, get_device_summary_str, get_inquirer_padding, get_log_prefix, s_if_plural, save_credential, service_to_protocol_str


async def pair_apple_tv(apple_tv: interface.BaseConfig, device_summary_str: str):
    """Perform pairing flow for provided apple_tv device"""
    print(f'{get_log_prefix()}Starting pairing flow for {device_summary_str}...')

    # Get protocol_strs for each service and print them
    service_protocol_strs = list(
        map(service_to_protocol_str, apple_tv.services))
    service_protocol_strs_formatted = ', '.join(service_protocol_strs)
    print(f'{get_log_prefix(False)}{apple_tv.name} supports {len(service_protocol_strs)} protocol{s_if_plural(len(service_protocol_strs))}: {service_protocol_strs_formatted}')

    if len(apple_tv.services):
        # Ask the user to confirm the device is on
        def validate_yes(_: list[str], current: str):
            if not current:
                raise inquirer.errors.ValidationError(
                    '', reason='Please power on {0:s}, wait, and then enter "y" to continue'.format(apple_tv.name))
            return True
        device_is_on = inquirer.Confirm(
            'device_is_on',
            message='{0:s}Is {1:s} powered on?'.format(
                get_inquirer_padding(), apple_tv.name),
            validate=validate_yes
        )
        inquirer.prompt([device_is_on],
                        raise_keyboard_interrupt=True)

    # Pair via each service, one-by-one
    for i in range(len(apple_tv.services)):
        service = apple_tv.services[i]
        protocol_str = service_protocol_strs[i]

        if not service.enabled:
            print(
                f'{get_log_prefix(False)}WARNING: Skipping {protocol_str} pairing for {apple_tv.name} because the service is disabled!', file=sys.stderr)
            continue

        # Initiate pairing
        print(
            f'{get_log_prefix()}Starting {protocol_str} pairing on {apple_tv.name}...')
        loop = asyncio.get_event_loop()
        pairing = await pair(apple_tv, service.protocol, loop)
        await pairing.begin()

        if pairing.device_provides_pin:
            # Ask for the PIN
            def validate_pin(_: str, current: str):
                if current != 'retry' and current != 'cancel' and re.search('^[0-9]{4}$', current) == None:
                    raise inquirer.errors.ValidationError(
                        '', reason='The PIN must be 4 digits')
                return True
            pairing_pin = inquirer.Text(
                'pairing_pin',
                message='{0:s}Enter the PIN from {1:s}'.format(
                    get_inquirer_padding(), apple_tv.name),
                validate=validate_pin
            )
            answers = inquirer.prompt(
                [pairing_pin], raise_keyboard_interrupt=True)
            pairing.pin(answers['pairing_pin'])
        else:
            # Generate a random PIN for the user to enter
            random_pin = str(randint(1, 9999)).zfill(4)
            pairing.pin(random_pin)

            # Ask the user to confirm they entered the PIN
            def validate_yes(_: list[str], current: str):
                if not current:
                    raise inquirer.errors.ValidationError(
                        '', reason='Enter "y" to continue')
                return True
            pairing_pin_entered = inquirer.Confirm(
                'pairing_pin_entered',
                message='{0:s}Enter this PIN: "{1:s}" on {1:s}'.format(
                    get_inquirer_padding(), random_pin, apple_tv.name),
                validate=validate_yes
            )
            inquirer.prompt([pairing_pin_entered],
                            raise_keyboard_interrupt=True)

        # Finish pairing and print result
        await pairing.finish()
        if pairing.has_paired:
            save_credential(apple_tv.device_info.mac, protocol_str,
                            pairing.service.credentials)
            print(
                f'{get_log_prefix(False)}{protocol_str} pairing on {apple_tv.name} completed successfully!')
        else:
            print(
                f'{get_log_prefix(False)}ERROR: {protocol_str} pairing on {apple_tv.name} failed!', file=sys.stderr)
            continue

        await pairing.close()

    print(f'{get_log_prefix()}Finished pairing flow for {device_summary_str}!')


async def pair_apple_tvs():
    """Scan for Apple TVs on network, ask which ones to pair, and pair one-by-one"""
    apple_tvs = await get_apple_tvs()
    device_summary_strs = list(map(get_device_summary_str, apple_tvs))

    idxs_to_pair = []
    if len(apple_tvs) > 1:
        # Ask which Apple TVs the user wants to pair, since there is more than one on the network
        def validate_some_checked(_: list[str], current: list[str]):
            if not current:
                raise inquirer.errors.ValidationError(
                    '', reason='You must select at least one Apple TV to pair!')
            return True
        check_to_pair = inquirer.Checkbox(
            'check_to_pair',
            message='{0:s}Which Apple TVs would you like to pair? (press space to check/uncheck, enter to proceed)'.format(
                get_inquirer_padding()),
            choices=device_summary_strs,
            validate=validate_some_checked
        )
        answers = inquirer.prompt(
            [check_to_pair], raise_keyboard_interrupt=True)

        def get_idx_from_summary_str(summary_str: str):
            return device_summary_strs.index(summary_str)
        idxs_to_pair = list(
            map(get_idx_from_summary_str, answers['check_to_pair']))
        idxs_to_pair.sort()
    else:
        # Assume the user wants to pair the one and only Apple TV on the network
        idxs_to_pair = [0]

    # Pair one-by-one
    for idx in idxs_to_pair:
        await pair_apple_tv(apple_tvs[idx], device_summary_strs[idx])

if __name__ == '__main__':
    asyncio.run(pair_apple_tvs())
