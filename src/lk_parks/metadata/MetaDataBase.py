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
    def best_plantnet_result(self) -> dict:
        return self.plantnet_results[0]

    @property
    def scientific_name(self) -> str:
        return self.best_plantnet_result['species']['scientificNameWithoutAuthor']
    
    @property
    def wikipedia_url(self) -> str:
        return 'https://en.wikipedia.org/wiki/' + self.scientific_name.replace(' ', '_')

    @property
    def family(self) -> str:
        return self.best_plantnet_result['species']['family']['scientificName']

    @property
    def common_names(self) -> list[str]:
        return self.best_plantnet_result['species']['commonNames']

    @property
    def confidence(self) -> float:
        return self.best_plantnet_result['score']
    
    @property
    def confidence_emoji(self) -> str:
        if self.confidence < 0.5:
            return '❓'
        return '🌳'

    @property
    def candidate_species_to_score(self) -> dict:
        return {result['species']['scientificNameWithoutAuthor']                : result['score'] for result in self.plantnet_results}

    @property
    def candidates_pretty(self) -> str:
        return ', '.join([f'{species} ({score:.1%})' for species,
                         score in self.candidate_species_to_score.items()])

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
    def sorter(self) -> int:
        lat, lng = self.latlng
        return int(lat * 1000 + lng)

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
        md_list = sorted(md_list, key=lambda md: md.sorter)
        return md_list
