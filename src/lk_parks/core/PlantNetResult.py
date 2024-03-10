import json
import os
import time
from dataclasses import dataclass

import requests
from utils import Log

from lk_parks.core.PlantPhotoBase import PlantPhoto
from lk_parks.core.taxonomy.Species import Species

log = Log('PlantNetResult')


@dataclass
class PlantNetResult:
    ut_api_call: int
    plant_photo: PlantPhoto
    species_to_score: dict[Species, float]

    URL_BASE = 'https://my-api.plantnet.org'
    MAX_RESULTS = 5
    T_DELAY = 1
    DEFAULT_PROJECT = 'all'
    DEFAULT_ORGANS = ['auto']

    # static methods
    @staticmethod
    def get_api_key() -> str:
        api_key = os.environ.get('PLANTNET_API_KEY')
        if not api_key:
            raise Exception('PLANTNET_API_KEY not set')
        return api_key

    @staticmethod
    def get_api_endpoint() -> str:
        return (
            PlantNetResult.URL_BASE
            + f'/v2/identify/{PlantNetResult.DEFAULT_PROJECT}'
            + f'?api-key={PlantNetResult.get_api_key()}'
        )

    @staticmethod
    def identify(image_path: str):
        time.sleep(PlantNetResult.T_DELAY)

        with open(image_path, "rb") as fin:
            request = requests.Request(
                'POST',
                url=PlantNetResult.get_api_endpoint(),
                files=[
                    ('images', (image_path, fin)),
                ],
                data={'organs': PlantNetResult.DEFAULT_ORGANS},
            )

            prepared = request.prepare()
            s = requests.Session()
            response = s.send(prepared)
            data = json.loads(response.text)
            results = data['results']
            n = len(results)
            log.debug(f'🪴Found {n} results with for {image_path}')
            return results

    @staticmethod
    def get_species_to_score(results: list) -> dict[Species, float]:
        species_to_score = {}
        for result in results:
            species = Species.from_plantnet_result(result)
            score = result['score']
            species_to_score[species] = score
        return species_to_score

    @staticmethod
    def from_photo(plant_photo: PlantPhoto) -> 'PlantNetResult':
        ut_api_call = int(time.time())
        results = PlantNetResult.identify(plant_photo.image_path)

        species_to_score = PlantNetResult.get_species_to_score(results)

        return PlantNetResult(ut_api_call, plant_photo, species_to_score)
