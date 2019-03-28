from tap_liveperson.streams.base import BaseEntityStream

import singer

LOGGER = singer.get_logger()  # noqa


class AgentGroupsStream(BaseEntityStream):
    API_METHOD = 'GET'
    SERVICE_NAME = 'accountConfigReadOnly'
    TABLE = 'agent_groups'

    @property
    def api_path(self):
        return (
            '/api/account/{}/configuration/le-users/agentGroups?include_deleted=true'
            .format(self.config.get('account_id')))

    def get_stream_data(self, result):
        return [
            self.transform_record(record)
            for record in result
        ]

    def get_pk_value(self, obj):
        return obj.get('id')
