from tap_liveperson.streams.base import BaseEntityStream

import singer

LOGGER = singer.get_logger()  # noqa


class AgentStatusStream(BaseEntityStream):
    API_METHOD = 'GET'
    SERVICE_NAME = 'accountConfigReadOnly'
    TABLE = 'agent_status'

    @property
    def api_path(self):
        return (
            '/api/account/{}/configuration/le-agents/status-reasons?include_deleted=true'
            .format(self.config.get('account_id')))

    def get_stream_data(self, result):
        return [
            self.transform_record(record)
            for record in result
        ]

    def get_pk_value(self, obj):
        return obj.get('id')
