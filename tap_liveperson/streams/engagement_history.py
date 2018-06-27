from tap_liveperson.streams.base import BaseStream

import funcy


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
        return result.get('interactionHistoryRecords')

    def get_pk_value(self, obj):
        return obj.get('info').get('engagementId')

    def convert_dates(self, obj):
        paths = [
            ('info', 'startTime',),
            ('info', 'endTime',),
            ('messageRecords', 'time',),
            ('agentParticipants', 'time',),
            ('consumerParticipant', 'time',),
            ('transfers', 'time',),
            ('interactions', 'interactionTime',),
            ('messageScore', 'time',),
            ('messageStatuses', 'time'),
            ('coBrowseSessions', 'startTime',),
            ('coBrowseSessions', 'endTime',),
        ]

        for path in paths:
            if isinstance(obj.get(path[0]), list):
                obj[path[0]] = [funcy.update_in(item, path[1:], self.convert_date)
                                for item in obj.get(path[0])]
            else:
                obj = funcy.update_in(obj, path, self.convert_date)

        return obj
