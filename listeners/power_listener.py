# See documentation: https://pyatv.dev/development/listeners/#power-state-updates

import asyncio
from pyatv import const, interface
from time import time

import config
import utils


def get_log_prefix(include_time: bool = True):
    return utils.get_log_prefix(include_time, "PowerListener")


class PowerListener(interface.PowerListener):
    last_power_on_time: int = 0
    prev_stable_state: const.PowerState

    def __init__(self, initial_power_state: const.PowerState):
        self.prev_stable_state = initial_power_state
        print(
            f'{get_log_prefix()}Initialized with initial_power_state: {initial_power_state}')

    def powerstate_update(self, _: const.PowerState, new_state: const.PowerState):
        now_time = int(time())
        # Consider power state change stable if:
        #   1. New power state is On or Off
        #   - AND -
        #   2. New power state is different from the previous stable state
        is_stable_change = (new_state == const.PowerState.On or new_state ==
                            const.PowerState.Off) and self.prev_stable_state != new_state

        if new_state == const.PowerState.On:
            self.last_power_on_time = now_time
        elif new_state == const.PowerState.Off:
            # When powering on Apple TV, the power_state alternates between On and Off for about 30 seconds
            #   To improve stability, off state changes that happen within config.POWER_OFF_STABLE_AFTER_SECONDS
            #   after the last On state change are ignored.
            # Since the power_state alternates, as described above, add an additional condition so that
            #   the state is only consider stable if it has been POWER_OFF_STABLE_AFTER_SECONDS or longer since the last power on
            is_stable_change = is_stable_change and now_time - \
                self.last_power_on_time >= config.POWER_OFF_STABLE_AFTER_SECONDS

        if is_stable_change:
            print(
                f'{get_log_prefix()}Stable update: {new_state}')
            self.prev_stable_state = new_state
            asyncio.ensure_future(utils.publish_event_to_ifttt_webhooks(
                'atv_power_on' if new_state == const.PowerState.On else 'atv_power_off'))
        else:
            print(
                f'{get_log_prefix()}Ignoring unstable update: {new_state}')
