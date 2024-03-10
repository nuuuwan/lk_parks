import json
import os
import time
from dataclasses import dataclass

import requests
from utils import JSONFile, Log

from lk_parks.core.plant_photo.PlantPhoto import PlantPhoto
from lk_parks.core.taxonomy.Species import Species
from lk_parks.metadata.MetaData import MetaData

log = Log('PlantNetResult')


@dataclass
class PlantNetResult:
    ut_api_call: int
    plant_photo_id: str
    species_name_to_score: dict[str, float]

    URL_BASE = 'https://my-api.plantnet.org'
    MAX_RESULTS = 5
    T_DELAY = 1
    DEFAULT_PROJECT = 'all'
    DEFAULT_ORGANS = ['auto']
    DIR_DATA_PLANT_NET_RESULTS = os.path.join( 'data',
            'plant_net_results',)

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
    def identify_from_legacy_metadata(image_path: str) -> list:
        metadata_path = MetaData.get_metadata_path(image_path)
        if not os.path.exists(metadata_path):
            return None

        metadata = JSONFile(metadata_path).read()
        results = metadata.get('plantnet_results', None)
        return results

    @staticmethod
    def identify_from_api(image_path: str):
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
    def identify(image_path: str) -> list:
        results = PlantNetResult.identify_from_legacy_metadata(image_path)
        if results:
            return results
        return PlantNetResult.identify_from_api(image_path)

    @staticmethod
    def get_species_name_to_score(results: list) -> dict[Species, float]:
        species_name_to_score = {}
        for result in results:
            species = Species.from_plant_net_raw_result(result)
            score = result['score']
            species_name_to_score[species.name] = score
        return species_name_to_score

    @staticmethod
    def from_plant_photo(plant_photo: PlantPhoto) -> 'PlantNetResult':
        if os.path.exists(PlantNetResult.get_data_path(plant_photo.id)):
            return PlantNetResult.from_plant_photo_id(plant_photo.id)

        ut_api_call = 0
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
        for plant_photo in plant_photo_list:
            PlantNetResult.from_plant_photo(plant_photo)
        log.info('build_from_plant_photos: done')
