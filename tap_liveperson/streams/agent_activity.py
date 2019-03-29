from tap_liveperson.streams.base import BaseFileStream

import singer
import json

LOGGER = singer.get_logger()  # noqa


class AgentActivityStream(BaseFileStream):
    API_METHOD = 'GET'
    SERVICE_NAME = None
    TABLE = 'agent_activity'

    def get_domain(self):
        return 'lo.da.liveperson.net'

    @property
    def api_path(self):
        return (
            '/data_access_le/account/{}/le/agentActivity'
            .format(self.config.get('account_id')))

    def get_stream_data(self, result):
        results = []

        for record in result:
            meta = record['metaData']['com.liveperson.dataaccess.MetaData']
            _meta = {
                "startTime": meta['startTime']['long'],
                "endTime": meta['endTime']['long'],
            }
            items = record['recordCollection']['array']
            for item in items:
                data = item['body']['com.liveperson.dataaccess.AgentActivityData']['agentSessionsData']['array']
                for payload in data:
                    payload['_meta'] = _meta
                    payload['id'] = '{}:{}'.format(payload['agentID']['long'], payload['timestamp']['long'])
                    transformed = self.transform_record(payload)
                    results.append(payload)
        return results
