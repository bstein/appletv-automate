# See documentation: https://pyatv.dev/development/listeners/#device-updates

from pyatv import interface

import utils


def get_log_prefix(include_time: bool = True):
    return utils.get_log_prefix(include_time, "DeviceListener")


class DeviceListener(interface.DeviceListener):
    def connection_lost(self, exception):
        print(f'{get_log_prefix()}connection_lost(): {exception}')

    def connection_closed(self):
        print(f'{get_log_prefix()}connection_closed()')
        print("Connection closed!")
