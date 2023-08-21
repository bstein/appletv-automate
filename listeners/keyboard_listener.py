# See documentation: https://pyatv.dev/development/listeners/#keyboard-updates

from pyatv import interface

import utils


def get_log_prefix(include_time: bool = True):
    return utils.get_log_prefix(include_time, "KeyboardListener")


class KeyboardListener(interface.KeyboardListener):
    def focusstate_update(self, old_state, new_state):
        print(
            f'{get_log_prefix()}focusstate_update() - changed from {old_state} to {new_state}')
