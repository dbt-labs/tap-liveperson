import requests
import requests_oauthlib
import singer
import singer.metrics

LOGGER = singer.get_logger()  # noqa


class LivepersonClient:

    MAX_TRIES = 5

    def __init__(self, config):
        self.config = config

    def get_authorization(self):
        return requests_oauthlib.OAuth1(
            self.config.get('app_key'),
            self.config.get('app_secret'),
            self.config.get('access_token'),
            self.config.get('access_token_secret'))

    def make_request(self, url, method, params=None, body=None):
        auth = self.get_authorization()

        LOGGER.info("Making {} request to {}".format(method, url))

        response = requests.request(
            method,
            url,
            headers={
                'Content-Type': 'application/json'
            },
            auth=auth,
            params=params,
            json=body)

        if response.status_code != 200:
            raise RuntimeError(response.text)

        return response.json()

    def get_service_domain(self, service_name):
        url = "http://api.liveperson.net/api/account/{account_id}/service/{service_name}/baseURI.json"  # noqa

        result = self.make_request(
            url.format(account_id=self.config.get('account_id'),
                       service_name=service_name),
            'GET',
            {'version': '1.0'})

        return result.get('baseURI')
