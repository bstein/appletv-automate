# The number of seconds to scan the network for Apple TV devices for
SCAN_TIMEOUT_SECONDS: int = 5

# The number of seconds after the most recent On state change required for treating an Off state change as stable (see comments in ./listeners/power_listener.py)
POWER_OFF_STABLE_AFTER_SECONDS: int = 20

# The IFTTT-provided API key required for sending requests for Webhooks integrations (see: https://ifttt.com/maker_webhooks)
IFTTT_API_KEY: str = ''
