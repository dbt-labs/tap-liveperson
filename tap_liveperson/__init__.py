#!/usr/bin/env python3

import argparse
import json
import sys

import singer

from tap_liveperson.catalog import is_selected, load_catalog
from tap_liveperson.client import LivepersonClient
from tap_liveperson.config import load_config
from tap_liveperson.state import load_state, save_state

from tap_liveperson.streams import AVAILABLE_STREAMS

LOGGER = singer.get_logger()  # noqa


def do_discover(args):
    LOGGER.info("Starting discovery.")

    config = args.config
    state = args.state

    catalog = []

    for available_stream in AVAILABLE_STREAMS:
        stream = available_stream(config, state, None, None)

        catalog += stream.generate_catalog()

    json.dump({'streams': catalog}, sys.stdout, indent=4)


def get_streams_to_replicate(config, state, catalog, client):
    streams = []

    for stream_catalog in catalog.get('streams'):
        if not is_selected(stream_catalog.get('schema', {})):
            LOGGER.info("'{}' is not marked selected, skipping."
                        .format(stream_catalog.get('stream')))
            continue

        for available_stream in AVAILABLE_STREAMS:
            if available_stream.matches_catalog(stream_catalog):
                streams.append(available_stream(
                    config, state, stream_catalog, client))

                break

    return streams


def do_sync(args):
    LOGGER.info("Starting sync.")

    config = args.config
    state = args.state
    catalog = args.properties
    client = LivepersonClient(config)

    streams = get_streams_to_replicate(config, state, catalog, client)

    for stream in streams:
        try:
            stream.state = state
            stream.sync()
            state = stream.state
        except OSError as e:
            LOGGER.error(str(e))
            exit(e.errno)

        except Exception as e:
            LOGGER.error(str(e))
            LOGGER.error('Failed to sync endpoint {}, moving on!'
                         .format(stream.TABLE))

    save_state(state)


@singer.utils.handle_top_exception(LOGGER)
def main():
    args = singer.utils.parse_args(
        required_config_keys=['app_key', 'app_secret',
                              'access_token', 'access_token_secret'])

    if args.discover:
        do_discover(args)
    else:
        do_sync(args)


if __name__ == '__main__':
    main()
