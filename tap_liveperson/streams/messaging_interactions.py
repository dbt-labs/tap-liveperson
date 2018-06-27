from tap_liveperson.streams.base import BaseStream

import funcy


class MessagingInteractionsStream(BaseStream):
    API_METHOD = 'POST'
    SERVICE_NAME = 'msgHist'
    TABLE = 'messaging_interactions'

    @property
    def api_path(self):
        return (
            '/messaging_history/api/account/{}/conversations/search'
            .format(self.config.get('account_id')))

    def get_stream_data(self, result):
        return result.get('conversationHistoryRecords')

    def get_pk_value(self, obj):
        return obj.get('info').get('conversationId')

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
            obj = funcy.update_in(obj, path, self.convert_date)

        return obj
