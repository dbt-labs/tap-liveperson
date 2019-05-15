from tap_liveperson.streams.base import RealtimeStream


class QueueHealthStream(RealtimeStream):
    API_METHOD = 'GET'
    SERVICE_NAME = 'leDataReporting'
    TABLE = 'queue_health'

    @property
    def api_path(self):
        return (
            '/operations/api/account/{}/queuehealth'
            .format(self.config.get('account_id')))

    def get_params(self):
        return {
            "timeframe": 1440,
            "interval": 5,
            "skillIds": "all"
        }

    def get_stream_data(self, result):
        if result['meta']['responseCode'] != 200:
            raise RuntimeError("Bad response code: {}".format(result['meta']))

        metrics_body = result.get('body', {})
        metrics_by_skill = metrics_body.get('metricsByIntervals', [])

        transformed = []
        for records in metrics_by_skill:
            timestamp = records['timestamp']
            for skill, data in records['metricsData']['skillsMetrics'].items():
                new_row = self.transform_record(data)

                new_row['id'] = self.get_pk_value(skill, timestamp)
                new_row['skill'] = skill
                new_row['timestamp'] = timestamp

                transformed.append(new_row)

        return transformed

    def get_pk_value(self, skill, timestamp):
        return "{}@{}".format(skill, timestamp)
