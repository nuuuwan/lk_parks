from dataclasses import dataclass
from functools import cached_property

from utils import Log

log = Log('MetaDataBasePlantNet')


@dataclass
class MetaDataBasePlantNet:

    @cached_property
    def best_plantnet_result(self) -> dict:
        return self.plantnet_results[0]

    @cached_property
    def species_data(self) -> dict:
        return self.best_plantnet_result['species']

    @cached_property
    def scientific_name(self) -> str:
        return self.species_data['scientificNameWithoutAuthor']

    @cached_property
    def authorship(self) -> str:
        return self.species_data['scientificNameAuthorship']

    @cached_property
    def wikipedia_url(self) -> str:
        return 'https://en.wikipedia.org/wiki/' + \
            self.scientific_name.replace(' ', '_')

    @cached_property
    def family(self) -> str:
        return self.species_data['family']['scientificName']

    @cached_property
    def genus(self) -> str:
        return self.species_data['genus']['scientificName']

    @cached_property
    def common_names(self) -> list[str]:
        return self.species_data['commonNames']

    @cached_property
    def confidence(self) -> float:
        return self.best_plantnet_result['score']

    @cached_property
    def confidence_emoji(self) -> str:
        if self.confidence < 0.5:
            return '❓'
        return '🌳'

    @cached_property
    def species_to_score(self) -> dict:
        idx = {}
        for x in self.plantnet_results[1:]:
            idx[x['species']['scientificNameWithoutAuthor']] = x['score']
        return idx

    @cached_property
    def other_candidates_pretty(self) -> str:
        def format_item(item):
            species, score = item
            return f'{species} ({score:.1%})'
        return ', '.join([format_item(x)
                         for x in self.species_to_score.items()])
