import json
import singer

LOGGER = singer.get_logger()  # noqa


def is_selected(catalog_entry):
    default = catalog_entry.get('selected-by-default', False)

    return ((catalog_entry.get('inclusion') == 'automatic') or
            (catalog_entry.get('inclusion') == 'available' and
             catalog_entry.get('selected', default) is True))


def load_catalog(filename):
    catalog = {}

    try:
        with open(filename) as handle:
            catalog = json.load(handle)
    except Exception:
        LOGGER.fatal("Failed to decode catalog file. Is it valid json?")
        raise RuntimeError

    return catalog
