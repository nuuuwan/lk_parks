import os
from dataclasses import dataclass
from functools import cache

from utils import TIME_FORMAT_TIME, JSONFile, Log, Time

log = Log('MetaData')


@dataclass
class MetaDataBase:
    original_image_path: str
    image_path: str
    ut: int
    latlng: tuple[float, float]
    alt: float
    direction: float
    plantnet_results: list[dict]

    DIR_DATA_METADATA = os.path.join('data', 'metadata')

    def __dict__(self) -> dict:
        return dict(
            original_image_path=self.original_image_path,
            image_path=self.image_path,
            ut=self.ut,
            latlng=self.latlng,
            alt=self.alt,
            direction=self.direction,
            plantnet_results=self.plantnet_results,
        )

    @property
    def time_str(self) -> str:
        return TIME_FORMAT_TIME.stringify(Time(self.ut))

    @property
    def image_path_unix(self) -> str:
        return self.image_path.replace('\\', '/')

    @property
    def direction_humanized(self) -> str:
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
        return directions[round(self.direction / 45) % 8]

    @property
    def direction_pretty(self) -> str:
        if not self.direction:
            return 'Unknown'
        return f'{self.direction:.1f}° ({self.direction_humanized})'

    @property
    def metadata_path(self) -> str:
        name_only = os.path.basename(self.image_path).split('.')[0]
        return os.path.join(MetaDataBase.DIR_DATA_METADATA,
                            name_only + '.json')

    def write(self):
        if os.path.exists(self.metadata_path):
            log.debug(f'Skipping {self.metadata_path}')
            return
        data = self.__dict__()
        JSONFile(self.metadata_path).write(data)
        log.debug(f'Wrote {self.metadata_path}')

    @property
    def cmp(self) -> int:
        lat, lng = self.latlng
        return lat * 1000 + lng

    @classmethod
    @cache
    def list_all(cls):
        md_list = []
        for file_name in os.listdir(MetaDataBase.DIR_DATA_METADATA):
            if file_name.endswith('.json'):
                metadata_path = os.path.join(
                    MetaDataBase.DIR_DATA_METADATA, file_name
                )
                data = JSONFile(metadata_path).read()
                md = cls(**data)
                md_list.append(md)
        md_list = sorted(md_list, key=lambda md: md.cmp, reverse=True)
        return md_list

    @classmethod
    @cache
    def summary(cls) -> dict:
        md_list = cls.list_all()

        def count(key_lambda):
            key_to_n = {}
            for md in cls.list_all():
                key = key_lambda(md)
                if key not in key_to_n:
                    key_to_n[key] = 0
                key_to_n[key] += 1
            sorted_key_to_n = dict(
                sorted(
                    key_to_n.items(),
                    key=lambda item: item[1],
                    reverse=True))
            return sorted_key_to_n

        return dict(
            n=len(md_list),
            family_to_n=count(lambda md: md.family),
            genus_to_n=count(lambda md: f'{md.genus} ({md.family})'),
            species_to_n=count(lambda md: md.scientific_name),
        )
