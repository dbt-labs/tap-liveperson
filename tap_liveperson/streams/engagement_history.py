from tap_liveperson.streams.base import BaseStream

import funcy
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
        return result.get('interactionHistoryRecords')

    def get_pk_value(self, obj):
        return obj.get('info').get('engagementId')

    def convert_dates(self, obj):
        paths = [
            ('info', 'startTime',),
            ('info', 'endTime',),
            ('coBrowseSessions', 'startTime',),
            ('coBrowseSessions', 'endTime',),
            ('surveys', 'preChat', 'time',),
            ('surveys', 'postChat', 'time',),
            ('transcript', 'lines', 'time',),
        ]

        for path in paths:
            last = path[-1]
            rest = path[:-1]
            items = funcy.get_in(obj, rest)

            if isinstance(items, list) and items:
                updated_items = [
                    funcy.update_in(item, [last], self.convert_date)
                    for item in items
                ]
                obj = funcy.set_in(obj, rest, updated_items)

            elif funcy.get_in(obj, path) is not None:
                obj = funcy.update_in(obj, path, self.convert_date)

        return obj
