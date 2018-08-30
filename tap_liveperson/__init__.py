#!/usr/bin/env python3

import singer

import tap_framework

from tap_liveperson.client import LivepersonClient
from tap_liveperson.streams import AVAILABLE_STREAMS

LOGGER = singer.get_logger()  # noqa


class LivepersonRunner(tap_framework.Runner):
    pass


@singer.utils.handle_top_exception(LOGGER)
def main():
    args = singer.utils.parse_args(
        required_config_keys=['app_key', 'app_secret',
                              'access_token', 'access_token_secret',
                              'account_id'])

    client = LivepersonClient(args.config)

    runner = LivepersonRunner(
        args, client, AVAILABLE_STREAMS)

    if args.discover:
        runner.do_discover()
    else:
        runner.do_sync()


if __name__ == '__main__':
    main()
