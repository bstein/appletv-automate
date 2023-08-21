# See documentation: https://pyatv.dev/development/listeners/#push-updates

from pyatv import interface

import utils


def get_log_prefix(include_time: bool = True):
    return utils.get_log_prefix(include_time, "PushListener")


class PushListener(interface.PushListener):
    prev_playstatus: interface.Playing

    def playstatus_update(self, updater, playstatus: interface.Playing):
        print(f'{get_log_prefix()}playstatus_update():\n{playstatus}')
        self.prev_playstatus = playstatus

    def playstatus_error(self, updater, exception: Exception):
        print(f'{get_log_prefix()}playstatus_error():\n{exception}')
