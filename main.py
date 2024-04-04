from aioconsole import ainput
import asyncio
import platform
from signal import SIGINT, SIGTERM
import sys

from connect_apple_tv import connect_apple_tv
from listeners.audio_listener import AudioListener
from listeners.device_listener import DeviceListener
from listeners.keyboard_listener import KeyboardListener
from listeners.power_listener import PowerListener
from listeners.push_listener import PushListener
from utils import get_log_prefix


loop = asyncio.get_event_loop()


async def main():
    """Guide user through pair & connect, add listeners, and exit on keyboard interrupt."""
    exit_code = 0
    connected_apple_tv = None
    try:
        connected_apple_tv = await connect_apple_tv()

        # TODO: Comment/uncomment the following lines depending on which listeners you'd like to use
        # For more information, see: https://pyatv.dev/development/listeners/
        # AudioListener
        # audio_listener = AudioListener()
        # connected_apple_tv.audio.listener = audio_listener

        # DeviceListener
        device_listener = DeviceListener()
        connected_apple_tv.listener = device_listener

        # KeyboardListener
        # keyboard_listener = KeyboardListener()
        # connected_apple_tv.keyboard.listener = keyboard_listener

        # PowerListener
        power_listener = PowerListener(connected_apple_tv.power.power_state)
        connected_apple_tv.power.listener = power_listener

        # PushListener
        # push_listener = PushListener()
        # connected_apple_tv.push_updater.listener = push_listener
        # connected_apple_tv.push_updater.start()

        print(
            f'{get_log_prefix()}Successfully added listeners!')

        if platform.system() == 'Windows':
            should_exit: bool = False
            include_time: bool = False
            while not should_exit:
                user_input: str = await ainput(f'{get_log_prefix(include_time)}Type "exit" to close connection and exit\n')
                include_time = True
                should_exit = user_input.strip() == 'exit'
        else:
            print(
                f'{get_log_prefix(False)}Press Ctrl+C to close connection and exit')
            # Attach signal handlers to trigger exit event when killed or terminated
            exit_event = asyncio.Event()
            for signal in [SIGINT, SIGTERM]:
                loop.add_signal_handler(signal, exit_event.set)
            await exit_event.wait()

        print()
    except KeyboardInterrupt:
        exit_code = 130
    except Exception as ex:
        exit_code = 1
        print(
            f'{get_log_prefix()}ERROR: An exception was thrown in main.py! Details:\n{ex}', sys.stderr)
    finally:
        print(f'{get_log_prefix()}Closing connection and exiting...')
        if connected_apple_tv:
            connected_apple_tv.close()
        exit(exit_code)


loop.run_until_complete(main())
