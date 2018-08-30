from tap_liveperson.streams.base import BaseStream

import singer

LOGGER = singer.get_logger()  # noqa


class EngagementHistoryStream(BaseStream):
    API_METHOD = 'POST'
    SERVICE_NAME = 'engHistDomain'
    TABLE = 'engagement_history'

    @property
    def api_path(self):
        return (
            '/interaction_history/api/account/{}/interactions/search'
            .format(self.config.get('account_id')))

    def get_stream_data(self, result):
        return [
            self.transform_record(record)
            for record in result.get('interactionHistoryRecords')
        ]

    def get_pk_value(self, obj):
        return obj.get('info').get('engagementId')
