import json
import os
import time
from functools import cache

import requests
from utils import Log

log = Log('PlantNet')


class PlantNet:
    URL_BASE = 'https://my-api.plantnet.org'
    MAX_RESULTS = 5
    T_DELAY = 1

    def __init__(self, api_key):
        self.api_key = api_key

    # @staticmethod
    # def from_args() -> 'PlantNet':
    #     parser = argparse.ArgumentParser()
    #     parser.add_argument('--plantnet_api_key', type=str, required=True)
    #     args = parser.parse_args()
    #     return PlantNet(args.api_key, args.project)

    @staticmethod
    def from_env() -> 'PlantNet':
        api_key = os.environ['PLANTNET_API_KEY']
        return PlantNet(api_key)

    @property
    def project(self) -> str:
        return 'all'

    @property
    def api_endpoint(self) -> str:
        return (
            PlantNet.URL_BASE
            + f'/v2/identify/{self.project}'
            + f'?api-key={self.api_key}'
        )

    @staticmethod
    def sleep():
        # log.debug(f'😴 Sleeping for {PlantNet.T_DELAY}s...')
        time.sleep(PlantNet.T_DELAY)

    @cache
    def identify(self, image_path: str) -> dict:
        PlantNet.sleep()

        with open(image_path, "rb") as fin:
            request = requests.Request(
                'POST',
                url=self.api_endpoint,
                files=[
                    ('images', (image_path, fin)),
                ],
                data={'organs': ['auto']},
            )

            prepared = request.prepare()
            s = requests.Session()
            response = s.send(prepared)
            data = json.loads(response.text)
            results = data['results']
            n = len(results)
            log.debug(f'🪴Found {n} results with for {image_path}')
            results = results[: PlantNet.MAX_RESULTS]
            return results
