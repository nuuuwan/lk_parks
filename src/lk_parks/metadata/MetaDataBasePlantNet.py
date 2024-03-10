from dataclasses import dataclass

from utils import Log

log = Log('MetaDataBasePlantNet')


@dataclass
class MetaDataBasePlantNet:

    @property
    def best_plantnet_result(self) -> dict:
        return self.plantnet_results[0]

    @property
    def species_data(self) -> dict:
        return self.best_plantnet_result['species']

    @property
    def scientific_name(self) -> str:
        return self.species_data['scientificNameWithoutAuthor']

    @property
    def authorship(self) -> str:
        return self.species_data['scientificNameAuthorship']

    @property
    def family(self) -> str:
        return self.species_data['family']['scientificName']

    @property
    def genus(self) -> str:
        return self.species_data['genus']['scientificName']

    @property
    def common_names(self) -> list[str]:
        return self.species_data['commonNames']

    @property
    def confidence(self) -> float:
        return self.best_plantnet_result['score']

    @property
    def confidence_emoji(self) -> str:
        if self.confidence < 1 / 3:
            return '🟥'
        if self.confidence < 2 / 3:
            return '🟨'
        return '🟩'

    @property
    def species_name_to_score(self) -> dict:
        idx = {}
        for x in self.plantnet_results:
            idx[x['species']['scientificNameWithoutAuthor']] = x['score']
        return idx
