import os
from dataclasses import dataclass
from functools import cache

from utils import TIME_FORMAT_TIME, JSONFile, Log, Time

log = Log('MetaData')


@dataclass
class MetaData:
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
    def google_maps_link(self) -> str:
        lat, lng = self.latlng
        url = f'https://www.google.com/maps/place/{lat}N,{lng}E'
        label = f'{lat:.4f}°N,{lng:.4f}°E'
        return f'[{label}]({url})'

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
    def description_lines(self):
        return [
            '|  |  |',
            '| --- | --- |',
            f'| **Time** | {self.time_str} |',
            f'| **Location** | {self.google_maps_link} |',
            f'| **Altitude** | {self.alt:.1f}m |',
            f'| **Camera Direction** | {self.direction_pretty} |',
        ]

    @property
    def title(self) -> str:
        return f'🌳 {self.google_maps_link} ({self.time_str})'

    @property
    def metadata_path(self) -> str:
        name_only = os.path.basename(self.image_path).split('.')[0]
        return os.path.join(MetaData.DIR_DATA_METADATA, name_only + '.json')

    def write(self):
        if os.path.exists(self.metadata_path):
            log.debug(f'Skipping {self.metadata_path}')
            return
        data = self.__dict__()
        JSONFile(self.metadata_path).write(data)
        log.debug(f'Wrote {self.metadata_path}')

    @staticmethod
    @cache
    def list_all():
        md_list = []
        for file_name in os.listdir(MetaData.DIR_DATA_METADATA):
            if file_name.endswith('.json'):
                metadata_path = os.path.join(
                    MetaData.DIR_DATA_METADATA, file_name
                )
                data = JSONFile(metadata_path).read()
                md = MetaData(**data)
                md_list.append(md)
        return md_list
