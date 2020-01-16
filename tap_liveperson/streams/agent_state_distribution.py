from tap_liveperson.streams.base import RealtimeStream


class AgentStateDistribution(RealtimeStream):
    API_METHOD = 'GET'
    SERVICE_NAME = 'leDataReporting'
    TABLE = 'agent_state_distribution'

    @property
    def api_path(self):
        return (
            '/operations/api/account/{}/agentactivity'
            .format(self.config.get('account_id')))

    def get_params(self):
        return {
            "timeframe": 1440,
            "interval": 5,
            "agentIds": "all",
            "v": 2
        }

    def get_stream_data(self, result):
        metrics_body = result.get('body', {})
        transformed = [
            self.transform_record(record)
            for record in metrics_body.get('metricsByIntervals', [])
        ]

        for record in transformed:
            record['id'] = self.get_pk_value(record)

        return transformed

    def get_pk_value(self, obj):
        return obj.get('timestamp')
