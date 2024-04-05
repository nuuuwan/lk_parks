import os
from dataclasses import dataclass
from functools import cached_property

from utils import JSONFile, Log

log = Log('PlantNetResultBase')


@dataclass
class PlantNetResultBase:
    ut_api_call: int
    plant_photo_id: str
    species_name_to_score: dict[str, float]

    @cached_property
    def top_species_name(self):
        if not self.species_name_to_score:
            return None
        return list(self.species_name_to_score.keys())[0]

    @cached_property
    def top_confidence(self):
        if not self.species_name_to_score:
            return None
        return list(self.species_name_to_score.values())[0]

    def to_dict(self) -> dict:
        return self.__dict__

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            ut_api_call=d['ut_api_call'],
            plant_photo_id=d['plant_photo_id'],
            species_name_to_score=d['species_name_to_score'],
        )

    @classmethod
    def from_plant_photo_id(cls, plant_photo_id: str):
        d = JSONFile(cls.get_data_path(plant_photo_id)).read()
        return cls.from_dict(d)

    @classmethod
    def get_data_path(cls, plant_photo_id: str) -> str:
        if not os.path.exists(cls.DIR_DATA_PLANT_NET_RESULTS):
            os.makedirs(cls.DIR_DATA_PLANT_NET_RESULTS)
        return os.path.join(
            cls.DIR_DATA_PLANT_NET_RESULTS,
            f'{plant_photo_id}.json',
        )

    @property
    def data_path(self) -> str:
        return self.get_data_path(self.plant_photo_id)

    def write(self):
        JSONFile(self.data_path).write(self.to_dict())
        log.info(f'Wrote {self.data_path}')
