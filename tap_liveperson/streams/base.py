import dateutil.parser
import math
import pytz
import singer
import singer.utils
import singer.metrics

from datetime import timedelta, datetime
from funcy import project
from tap_liveperson.config import get_config_start_date
from tap_liveperson.schemas import load_schema_by_name
from tap_liveperson.state import incorporate, save_state, \
    get_last_record_value_for_table

LOGGER = singer.get_logger()


class BaseStream:

    # ABSTRACT PROPERTIES -- SHOULD BE OVERRIDDEN
    TABLE = None

    def get_schema(self):
        return load_schema_by_name(self.TABLE)

    def get_stream_data(self, result):
        """
        Given a result set from Liveperson, return the data
        to be persisted for this stream.
        """
        raise RuntimeError("get_stream_data not implemented!")

    # GLOBAL PROPERTIES -- DON'T OVERRIDE
    KEY_PROPERTIES = ['id']

    def __init__(self, config, state, catalog, client):
        self.config = config
        self.state = state
        self.catalog = catalog
        self.client = client

    @classmethod
    def matches_catalog(cls, catalog):
        return catalog.get('stream') == cls.TABLE

    def generate_catalog(self):
        return [{
            'tap_stream_id': self.TABLE,
            'stream': self.TABLE,
            'key_properties': self.KEY_PROPERTIES,
            'schema': self.get_schema()
        }]

    def get_catalog_keys(self):
        return list(
            self.catalog.get('schema', {}).get('properties', {}).keys())

    def get_pk_value(self):
        raise NotImplementedError(
            '`get_pk_value` is not implemented for this stream!')

    def convert_date(self, date):
        # dates come in like "2018-02-22 20:38:49.628+0000"
        if date is None:
            return date

        try:
            return dateutil.parser.parse(date).isoformat('T')
        except ValueError:
            return None

    def filter_keys(self, obj):
        obj['id'] = self.get_pk_value(obj)
        return self.convert_dates(project(obj, self.get_catalog_keys()))

    def write_schema(self):
        singer.write_schema(
            self.catalog.get('stream'),
            self.catalog.get('schema'),
            key_properties=self.catalog.get('key_properties'))

    def get_domain(self):
        return self.client.get_service_domain(self.SERVICE_NAME)

    def sync(self):
        LOGGER.info('Syncing stream {} with {}'
                    .format(self.catalog.get('tap_stream_id'),
                            self.__class__.__name__))

        self.write_schema()

        return self.sync_data()

    def sync_data(self):
        table = self.TABLE

        date = get_last_record_value_for_table(self.state, table)

        if date is None:
            date = get_config_start_date(self.config)

        interval = timedelta(days=7)

        while date < datetime.now(pytz.utc):
            self.sync_data_for_period(date, interval)

            date = date + interval

        return self.state

    def get_pagination(self, page):
        page_size = 100
        return {
            'offset': 0 + (page_size * (page - 1)),
            'limit': page_size,
            'sort': 'start:asc',
        }

    def get_filters(self, start, end):
        return {
            'start': {
                'from': int(start.timestamp() * 1000),
                'to': int(end.timestamp() * 1000)
            }
        }

    def sync_data_for_period(self, date, interval):
        table = self.TABLE
        domain = self.get_domain()

        updated_after = date
        updated_before = updated_after + interval

        LOGGER.info(
            'Syncing data from {} to {}'.format(
                updated_after.isoformat(),
                updated_before.isoformat()))

        has_data = True
        page = 1
        offset = 0
        total_pages = -1

        while has_data:
            url = (
                'https://{domain}{api_path}'.format(
                    domain=domain,
                    api_path=self.api_path))

            params = self.get_pagination(page)
            body = self.get_filters(updated_after, updated_before)

            result = self.client.make_request(
                url, self.API_METHOD, params=params, body=body)

            count = result.get('_metadata', {}).get('count')

            total_pages = math.ceil(count / params['limit'])
            data = self.get_stream_data(result)

            with singer.metrics.record_counter(endpoint=table) as counter:
                for obj in data:
                    singer.write_records(
                        table,
                        [self.filter_keys(obj)])

                    counter.increment()

                    self.state = incorporate(self.state,
                                             table,
                                             'updated_at',
                                             obj.get('updated_at'))

            if count == 0 or page == total_pages:
                LOGGER.info('Reached end of stream, moving on.')
                has_data = False

            else:
                LOGGER.info('Synced page {} of {}'.format(page, total_pages))

            page = page + 1

        self.state = incorporate(self.state,
                                 table,
                                 'updated_at',
                                 date.isoformat())

        save_state(self.state)
