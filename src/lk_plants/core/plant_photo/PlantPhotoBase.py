import os
from dataclasses import dataclass

from utils import JSONFile, Log

from utils_future import LatLng

log = Log('PlantPhotoBase')


@dataclass
class PlantPhotoBase:
    id: str
    ut: int
    latlng: LatLng
    original_image_path: str
    image_path: str
    alt: float
    direction: float

    @classmethod
    def get_dir_data(cls):
        return os.path.join(
            'data',
            'plant_photos',
        )

    @classmethod
    def get_data_path(cls, id: str) -> str:
        return os.path.join(
            cls.get_dir_data(),
            f'{id}.json',
        )

    @property
    def data_path(self) -> str:
        return self.get_data_path(self.id)

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d['latlng'] = self.latlng.to_dict()
        return d

    def write(self):
        JSONFile(self.data_path).write(self.to_dict())
        log.debug(f'Wrote {self.data_path}')

    # static methods
    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            id=d['id'],
            ut=d['ut'],
            latlng=LatLng.from_dict(d['latlng']),
            original_image_path=d['original_image_path'],
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

    @staticmethod
    def build_contents():
        plant_photo_list = PlantPhotoBase.list_all()
        id_list = [plant_photo.id for plant_photo in plant_photo_list]
        sorted_id_list = sorted(id_list)
        contents_path = os.path.join(
            'data',
            'plant_photos.contents.json',
        )
        JSONFile(contents_path).write(sorted_id_list)
        n = len(sorted_id_list)
        log.info(f'Wrote {n} plant_photo ids to {contents_path}')
