from tap_liveperson.streams.base import BaseStream


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
        return [
            self.transform_record(record)
            for record in result.get('conversationHistoryRecords')
        ]

    def get_pk_value(self, obj):
        return obj.get('info').get('conversationId')
