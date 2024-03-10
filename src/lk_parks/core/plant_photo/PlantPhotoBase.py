import os
from dataclasses import dataclass

from utils import JSONFile, Log

from utils_future import LatLng

log = Log('PlantPhotoBase')


@dataclass
class PlantPhotoBase:
    ut: int
    latlng: LatLng
    image_original_path: str
    image_path: str
    alt: float
    direction: float

    @classmethod
    def get_data_path(cls, image_path: str) -> str:
        image_path_base = os.basename(image_path).split('.')[0]

        return os.path.join(
            'data',
            'plant_photos',
            f'{image_path_base}.json',
        )

    @property
    def data_path(self) -> str:
        return self.get_data_path(self.image_path)

    def write(self):
        JSONFile(self.data_path).write(self.to_dict())
        log.debug(f'Wrote {self.data_path}')

    # static methods
    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            ut=d['ut'],
            latlng=LatLng.from_dict(d['latlng']),
            image_original_path=d['image_original_path'],
            image_path=d['image_path'],
            alt=d['alt'],
            direction=d['direction'],
        )

    @classmethod
    def list_all(cls) -> list:
        plant_photo_list = []
        for file_name in os.listdir(
            os.path.join(
                'data',
                'plant_photos',
            )
        ):
            if not file_name.endswith('.json'):
                continue

            data_path = os.path.join(
                'data',
                'plant_photos',
                file_name,
            )
            d = JSONFile(data_path).read()
            plant_photo = cls.from_dict(d)
            plant_photo_list.append(plant_photo)
        return plant_photo_list
