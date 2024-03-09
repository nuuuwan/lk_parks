import os
from dataclasses import dataclass

from utils import JSONFile, Log, Time, TimeFormat

log = Log('MetaDataBase')


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

    TIME_FORMAT = TimeFormat('%H:%M %p (%b %d, %Y)')

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
        return MetaDataBase.TIME_FORMAT.stringify(Time(self.ut))

    @property
    def image_path_unix(self) -> str:
        return self.image_path.replace('\\', '/')

    @property
    def direction_humanized(self) -> str:
        directions = ['N', 'NNE', 'NE', 'ENE',
                      'E', 'ESE', 'SE', 'SSE',
                      'S', 'SSW', 'SW', 'WSW',
                      'W', 'WNW', 'NW', 'NNW']
        return directions[round(self.direction / 22.5) % 16]

    @property
    def direction_pretty(self) -> str:
        if not self.direction:
            return '(No Data)'
        return f'{self.direction:.1f}° ({self.direction_humanized})'

    @property
    def metadata_path(self) -> str:
        name_only = os.path.basename(self.image_path).split('.')[0]
        return os.path.join(MetaDataBase.DIR_DATA_METADATA,
                            name_only + '.json')

    @property
    def metadata_path_unix(self) -> str:
        return self.metadata_path.replace('\\', '/')

    def write(self):
        if os.path.exists(self.metadata_path):
            log.debug(f'Skipping {self.metadata_path}')
            return
        data = self.__dict__()
        JSONFile(self.metadata_path).write(data)
        log.debug(f'Wrote {self.metadata_path}')
