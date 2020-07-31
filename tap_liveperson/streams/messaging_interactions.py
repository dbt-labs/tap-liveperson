from tap_liveperson.streams.base import BaseStream


class MessagingInteractionsStream(BaseStream):
    API_METHOD = 'POST'
    SERVICE_NAME = 'msgHist'
    TABLE = 'messaging_interactions'

    CONTENT_TO_RETRIEVE = ['campaign', 'messageRecords', 'agentParticipants',
            'agentParticipantsLeave', 'agentParticipantsActive',
            'consumerParticipants', 'transfers', 'interactions',
            'messageScores', 'messageStatuses', 'conversationSurveys',
            'coBrowseSessions', 'summary', 'sdes', 'unAuthSdes', 'monitoring']

    @property
    def api_path(self):
        return (
            '/messaging_history/api/account/{}/conversations/search?v=2'
            .format(self.config.get('account_id')))

    def get_stream_data(self, result):
        recs = [record for record in result.get('conversationHistoryRecords')]

        for record in recs:
            record['id'] = self.get_pk_value(record)

        return recs

    def get_pk_value(self, obj):
        return obj.get('info').get('conversationId')
