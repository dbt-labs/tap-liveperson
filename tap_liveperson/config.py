import json
import singer

from dateutil.parser import parse

LOGGER = singer.get_logger()  # noqa


def validate_config(config):
    required_keys = [
        'app_key', 'app_secret', 'access_token', 'access_token_secret']
    missing_keys = []
    null_keys = []
    has_errors = False

    for required_key in required_keys:
        if required_key not in config:
            missing_keys.append(required_key)

        elif config.get(required_key) is None:
            null_keys.append(required_key)

    if missing_keys:
        LOGGER.fatal("Config is missing keys: {}"
                     .format(", ".join(missing_keys)))
        has_errors = True

    if null_keys:
        LOGGER.fatal("Config has null keys: {}"
                     .format(", ".join(null_keys)))
        has_errors = True

    if has_errors:
        raise RuntimeError


def load_config(filename):
    config = {}

    try:
        with open(filename) as handle:
            config = json.load(handle)
    except Exception:
        LOGGER.fatal("Failed to decode config file. Is it valid json?")
        raise RuntimeError

    validate_config(config)

    return config


def get_config_start_date(config):
    return parse(config.get('start_date'))
