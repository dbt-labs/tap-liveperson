import math
import pytz
import singer
import singer.utils
import singer.metrics

from datetime import timedelta, datetime

from tap_liveperson.config import get_config_start_date
from tap_liveperson.state import incorporate, save_state, \
    get_last_record_value_for_table

from tap_liveperson.unzip import unzip
from tap_framework.streams import BaseStream as base

LOGGER = singer.get_logger()


class BaseStream(base):

    # GLOBAL PROPERTIES -- DON'T OVERRIDE
    KEY_PROPERTIES = ['id']

    def get_pk_value(self):
        raise NotImplementedError(
            '`get_pk_value` is not implemented for this stream!')

    def get_domain(self):
        return self.client.get_service_domain(self.SERVICE_NAME)

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
                        [obj])

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

class BaseEntityStream(BaseStream):
    def get_params(self):
        return {}

    def get_body(self):
        return {}

    def sync_data(self):
        table = self.TABLE
        LOGGER.info('Syncing data for entity {}'.format(table))

        domain = self.get_domain()

        url = (
            'https://{domain}{api_path}'.format(
                domain=domain,
                api_path=self.api_path))

        params = self.get_params()
        body = self.get_body()

        result = self.client.make_request(
            url, self.API_METHOD, params=params, body=body)
        data = self.get_stream_data(result)

        with singer.metrics.record_counter(endpoint=table) as counter:
            for obj in data:
                singer.write_records(
                    table,
                    [obj])

                counter.increment()
        return self.state

class BaseFileStream(BaseStream):

    def get_filters(self, start, end):
        return {
            'startTime': int(start.timestamp() * 1000),
            'endTime': int(end.timestamp() * 1000)
        }

    def get_body(self):
        return {}

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

        url = (
            'https://{domain}{api_path}'.format(
                domain=domain,
                api_path=self.api_path))

        params = self.get_filters(updated_after, updated_before)
        body = self.get_body()

        try:
            result = self.client.make_request(
                url, self.API_METHOD, params=params, body=body)

        except RuntimeError as e:
            if hasattr(e, 'args') and len(e.args) > 0:
                if 'No Available Files' in e.args[0]:
                    LOGGER.info("No data available for {}-{}".format(updated_after, updated_before))
                    return
                else:
                    raise
            else:
                raise

        if 'dataAccessFiles' not in result:
            raise RuntimeError("Expected to see 'dataAccessFiles', but did not see it")

        files = result['dataAccessFiles']
        for file_dict in files['file']:
            name = file_dict['@name']
            start = file_dict['@scopeStartDate']
            end = file_dict['@scopeEndDate']
            href = file_dict['@href']
            file_results = unzip(self.client.download(href).content)

        data = self.get_stream_data(file_results)

        with singer.metrics.record_counter(endpoint=table) as counter:
            for obj in data:
                singer.write_records(
                    table,
                    [obj])

                counter.increment()

        LOGGER.info('Synced {} for {}'.format(updated_after, self.TABLE))

        self.state = incorporate(self.state,
                                 table,
                                 'updated_at',
                                 date.isoformat())

        save_state(self.state)


class RealtimeStream(BaseStream):
    def sync_data(self):
        table = self.TABLE

        domain = self.get_domain()
        params = self.get_params()

        LOGGER.info("Syncing realtime stream {} with params {}".format(table, params))

        url = 'https://{domain}{api_path}'.format(domain=domain, api_path=self.api_path)

        result = self.client.make_request(
            url, self.API_METHOD, params=params)

        data = self.get_stream_data(result)

        with singer.metrics.record_counter(endpoint=table) as counter:
            for obj in data:
                singer.write_records(
                    table,
                    [obj])

                counter.increment()

        return self.state
