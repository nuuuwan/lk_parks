import json
import os
import time

import requests
from utils import Log

from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto
from lk_plants.core.taxonomy.Species import Species

log = Log('PlantNetResultIdentify')


class PlantNetResultIdentify:
   
    URL_BASE = 'https://my-api.plantnet.org'

    T_DELAY = 1
    # DEFAULT_PROJECT = 'k-indian-subcontinent'
    DEFAULT_PROJECT = 'k-world-flora'
    # DEFAULT_PROJECT = 'all'

    FORCE_RETRY = False
    MIN_SCORE = 0.2

    # leaf, flower, fruit, bark, auto.
    DEFAULT_ORGAN = 'auto'

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
            PlantNetResultIdentify.URL_BASE
            + f'/v2/identify/{PlantNetResultIdentify.DEFAULT_PROJECT}'
            + f'?api-key={PlantNetResultIdentify.get_api_key()}'
        )

    @staticmethod
    def get_test_url() -> str:
        return (
            PlantNetResultIdentify.URL_BASE
            + '/v2/projects'
            + f'?lang=en&type=kt&api-key={PlantNetResultIdentify.get_api_key()}'
        )

    @staticmethod
    def identify(image_path: str):
        time.sleep(PlantNetResultIdentify.T_DELAY)

        with open(image_path, "rb") as fin:
            request = requests.Request(
                'POST',
                url=PlantNetResultIdentify.get_api_endpoint(),
                files=[
                    ('images', (image_path, fin)),
                ],
                data={'organs': [PlantNetResultIdentify.DEFAULT_ORGAN]},
            )

            prepared = request.prepare()
            s = requests.Session()
            response = s.send(prepared)
            data = json.loads(response.text)

            results = data.get('results', [])
            n = len(results)
            logger = log.debug if n > 0 else log.warn
            if n == 0:
                log.debug(PlantNetResultIdentify.get_test_url())
            logger(f'🪴 Found {n} results with for {image_path}')
            return results

    @staticmethod
    def get_species_name_to_score(results: list) -> dict[Species, float]:
        species_name_to_score = {}
        for i, result in enumerate(results):
            species = Species.from_plant_net_raw_result(result)
            score = result['score']
            species_name_to_score[species.name] = score

            if i < 5:
                emoji = ''
                if score >= PlantNetResultIdentify.MIN_SCORE:
                    emoji = '✅'
                log.debug(f'\t{score:.1%}: {species.name}{emoji}')
        return species_name_to_score

    @classmethod
    def filter_with_no_results(cls, plant_photo: PlantPhoto):
        return not os.path.exists(
            cls.get_data_path(plant_photo.id)
        )

    @classmethod
    def from_plant_photo(cls, plant_photo: PlantPhoto):
        if os.path.exists(
            cls.get_data_path(plant_photo.id)
        ):
            plant_net_result = cls.from_plant_photo_id(
                plant_photo.id
            )

            return plant_net_result

        ut_api_call = time.time()
        results = PlantNetResultIdentify.identify(plant_photo.image_path)
        species_name_to_score = (
            PlantNetResultIdentify.get_species_name_to_score(results)
        )

        plant_net_result = cls(
            ut_api_call, plant_photo.id, species_name_to_score
        )
        plant_net_result.write()
        return plant_net_result

    @classmethod
    def build_from_plant_photos(cls):
        plant_photo_list = PlantPhoto.list_all()
        plant_photo_list_filtered = [
            plant_photo
            for plant_photo in plant_photo_list
            if PlantNetResultIdentify.filter_with_no_results(plant_photo)
        ]
        n_filtered = len(plant_photo_list_filtered)
        log.debug(f'{n_filtered=}')

        for i, plant_photo in enumerate(plant_photo_list_filtered):
            log.debug(f'{i + 1}/{n_filtered}')
            try:
                cls.from_plant_photo(plant_photo)
            except Exception as e:
                log.error(e)
        log.info('build_from_plant_photos: done')
