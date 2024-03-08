from dataclasses import dataclass

from utils import Log

log = Log('MetaDataBasePlantNet')


@dataclass
class MetaDataBasePlantNet:

    IUCN_CATEGORY_TO_DESCRIPTION = {
        'EX': '⚫ Extinct',
        'EW': '🟤 Extinct in the Wild',
        'CR': '🔴 Critically Endangered',
        'EN': '🟠 Endangered',
        'VU': '🟡 Vulnerable',
        'NT': '🟡 Near Threatened',
        'CD': '🟡 Conservation Dependent',
        'LC': '🟢 Least Concern',
        'DD': '⚪ Data Deficient',
        'NE': '⚪ Not Evaluated',
    }

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
        if self.confidence < 0.5:
            return '❓'
        return '🌳'

    @property
    def species_to_score(self) -> dict:
        idx = {}
        for x in self.plantnet_results[1:]:
            idx[x['species']['scientificNameWithoutAuthor']] = x['score']
        return idx

    @property
    def other_candidates_pretty(self) -> str:
        def format_item(item):
            species, score = item
            return f'{species} ({score:.1%})'
        return ', '.join([format_item(x)
                         for x in self.species_to_score.items()])

    @property
    def gbif_id(self) -> str:
        return self.best_plantnet_result['gbif']['id']

    @property
    def gbif_url(self) -> str:
        return f'https://www.gbif.org/species/{self.gbif_id}'

    @property
    def powo_id(self) -> str:
        if 'powo' in self.best_plantnet_result:
            return self.best_plantnet_result['powo']['id']
        return None

    @property
    def powo_url(self) -> str:
        return f'https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:{self.powo_id}'

    @property
    def iucn_id(self) -> str:
        if 'iucn' in self.best_plantnet_result:
            return self.best_plantnet_result['iucn']['id']
        return None

    @property
    def iucn_url(self) -> str:
        url = 'https://www.iucnredlist.org/search' + \
            f'?query={self.scientific_name}' + '&searchType=species'
        url = url.replace(' ', '+')
        return url

    @property
    def iucn_category(self) -> str:
        if 'iucn' in self.best_plantnet_result:
            return self.best_plantnet_result['iucn']['category']
        return None

    @property
    def iucn_category_humanized(self) -> str:
        description = self.IUCN_CATEGORY_TO_DESCRIPTION.get(
            self.iucn_category, 'Unknown Category')
        return f'{description} ({self.iucn_category})'
