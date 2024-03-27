import json
import os
import time
from dataclasses import dataclass
from functools import cached_property

import requests
from utils import JSONFile, Log

from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto
from lk_plants.core.taxonomy.Species import Species

log = Log('PlantNetResult')


@dataclass
class PlantNetResult:
    ut_api_call: int
    plant_photo_id: str
    species_name_to_score: dict[str, float]

    URL_BASE = 'https://my-api.plantnet.org'

    T_DELAY = 1
    # DEFAULT_PROJECT = 'k-indian-subcontinent'
    # DEFAULT_PROJECT = 'k-world-flora'
    DEFAULT_PROJECT = 'all'

    FORCE_RETRY = True
    MIN_SCORE = 0.2

    # leaf, flower, fruit, bark, auto.
    DEFAULT_ORGAN = 'auto'    
    DIR_DATA_PLANT_NET_RESULTS = os.path.join(
        'data',
        'plant_net_results',
    )

    def to_dict(self) -> dict:
        return self.__dict__

    @staticmethod
    def from_dict(d: dict) -> 'PlantNetResult':
        return PlantNetResult(
            ut_api_call=d['ut_api_call'],
            plant_photo_id=d['plant_photo_id'],
            species_name_to_score=d['species_name_to_score'],
        )

    @staticmethod
    def from_plant_photo_id(plant_photo_id: str) -> 'PlantNetResult':
        d = JSONFile(PlantNetResult.get_data_path(plant_photo_id)).read()
        return PlantNetResult.from_dict(d)

    @classmethod
    def get_data_path(cls, plant_photo_id: str) -> str:
        if not os.path.exists(PlantNetResult.DIR_DATA_PLANT_NET_RESULTS):
            os.makedirs(PlantNetResult.DIR_DATA_PLANT_NET_RESULTS)
        return os.path.join(
            PlantNetResult.DIR_DATA_PLANT_NET_RESULTS,
            f'{plant_photo_id}.json',
        )

    @property
    def data_path(self) -> str:
        return self.get_data_path(self.plant_photo_id)

    def write(self):
        JSONFile(self.data_path).write(self.to_dict())
        log.info(f'Wrote {self.data_path}')

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
                data={'organs': [PlantNetResult.DEFAULT_ORGAN]},
            )

            prepared = request.prepare()
            s = requests.Session()
            response = s.send(prepared)
            data = json.loads(response.text)
            results = data.get('results', [])
            n = len(results)
            log.debug(f'🪴 Found {n} results with for {image_path}')
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
                if score >= PlantNetResult.MIN_SCORE:
                    emoji = '✅'
                log.debug(f'\t{score:.1%}: {species.name}{emoji}')
        return species_name_to_score

    @staticmethod
    def filter_with_no_results(plant_photo: PlantPhoto):
        return not os.path.exists(
            PlantNetResult.get_data_path(plant_photo.id)
        )

    @staticmethod
    def from_plant_photo(plant_photo: PlantPhoto) -> 'PlantNetResult':
        if os.path.exists(PlantNetResult.get_data_path(plant_photo.id)):
            plant_net_result = PlantNetResult.from_plant_photo_id(plant_photo.id)
            
            if not plant_net_result.FORCE_RETRY:
                return plant_net_result
            
            top_score = plant_net_result.top_score
            if top_score and top_score > PlantNetResult.MIN_SCORE:
                return plant_net_result
            log.warn(f'Re-trying {plant_photo.id} ({top_score:.1%})')
            
        ut_api_call = time.time()
        results = PlantNetResult.identify(plant_photo.image_path)
        species_name_to_score = PlantNetResult.get_species_name_to_score(
            results
        )

        plant_net_result = PlantNetResult(
            ut_api_call, plant_photo.id, species_name_to_score
        )
        plant_net_result.write()
        return plant_net_result

    @staticmethod
    def build_from_plant_photos():
        plant_photo_list = PlantPhoto.list_all()
        plant_photo_list_filtered = [
            plant_photo
            for plant_photo in plant_photo_list
            if PlantNetResult.filter_with_no_results(plant_photo)
        ]
        n_filtered = len(plant_photo_list_filtered)
        log.debug(f'{n_filtered=}')

        for i, plant_photo in enumerate(plant_photo_list_filtered):
            log.debug(f'{i + 1}/{n_filtered}')
            PlantNetResult.from_plant_photo(plant_photo)
        log.info('build_from_plant_photos: done')

    @cached_property
    def top_species_name(self):
        if not self.species_name_to_score:
            return None
        return list(self.species_name_to_score.keys())[0]

    @cached_property
    def top_score(self):
        if not self.species_name_to_score:
            return None
        return list(self.species_name_to_score.values())[0]
