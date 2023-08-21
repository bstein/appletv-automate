# appletv-automate

This repository includes a [Python](https://www.python.org/) CLI to pair, connect, and perform automations for events for Apple TVs on your local network by utilizing the [pyatv](https://github.com/postlund/pyatv) library.

Some barebones [listeners](https://github.com/bstein/appletv-automate/tree/master/listeners) classes are included. There is also a basic function named `publish_event_to_ifttt_webhooks()` in [utils.py](https://github.com/bstein/appletv-automate/blob/master/utils.py) which enables [IFTTT Webhooks integrations](https://ifttt.com/maker_webhooks).

The motivation behind this project was to enable running IFTTT applets when an Apple TV powered on or off. However, it has been written in a way which should make it extensible for other purposes. For example, you could perform some action when a movie starts playing. Please refer to the [pyatv documentation](https://pyatv.dev/development/listeners/) for information about available listeners.

## Requirements

- Python 3.7+
- Additional libraries defined in [requirements.txt](https://github.com/bstein/appletv-automate/blob/master/requirements.txt)
- OpenSSL compiled with support for ed25519 in order to connect to MRP devices ([more info](https://pyatv.dev/support/faq/#i-get-an-error-about-ed25519-is-not-supported-how-can-i-fix-that))

## Getting Started

1. Clone this repository:

   ```
   git clone https://github.com/bstein/appletv-automate.git
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Copy `config-sample.py` to `config.py` and update `IFTTT_API_KEY`, should you wish to use it.

4. Open `main.py` and find the `# TODO` comment. By default, the `PowerListener` is uncommented. Comment/uncomment the other listeners based on which ones you would like to use. You will likely want to tweak the listener classes to fit your needs, but you may use them as-is for now.

5. Start `main.py`. To quit, press `Ctrl+C`.

   ```
   python main.py
   ```
