# See documentation: https://pyatv.dev/development/listeners/#audio-updates

from pyatv import interface

import utils


def get_log_prefix(include_time: bool = True):
    return utils.get_log_prefix(include_time, "AudioListener")


class AudioListener(interface.AudioListener):
    def volume_update(self, old_level, new_level):
        print(
            f'{get_log_prefix()}volume_update() - changed from {old_level} to {new_level}')

    def outputdevices_update(self, old_devices, new_devices):
        print(
            f'{get_log_prefix()}outputdevices_update() - changed from {old_devices} to {new_devices}')
