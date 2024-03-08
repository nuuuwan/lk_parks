import os
from dataclasses import dataclass

from utils import File, Log

log = Log('MetaData')


@dataclass
class MetaDataREADME:
    README_PATH = os.path.join('README.md')

    @staticmethod
    def get_wiki_url(x):
        return 'https://en.wikipedia.org/wiki/' + \
            x.replace(' ', '_')

    @staticmethod
    def get_wiki_link(x):
        return f'[{x}]({MetaDataREADME.get_wiki_url(x)})'

    @property
    def common_names_pretty(self) -> str:
        if not self.common_names:
            return '-'
        return ', '.join(self.common_names)

    @property
    def title(self) -> str:
        return f'{self.confidence_emoji}' + \
            f' {self.scientific_name_link} ({self.google_maps_link})'

    @property
    def google_maps_link(self) -> str:
        lat, lng = self.latlng
        url = f'https://www.google.com/maps/place/{lat}N,{lng}E'
        label = f'{lat:.4f}°N,{lng:.4f}°E'
        return f'[{label}]({url})'

    @property
    def gbif_pretty(self) -> str:
        if not self.gbif_id:
            return 'Unknown'
        return f'[{self.gbif_id}]({self.gbif_url})'

    @property
    def powo_pretty(self) -> str:
        if not self.powo_id:
            return 'Unknown'
        return f'[{self.powo_id}]({self.powo_url})'

    @property
    def iucn_pretty(self) -> str:
        if not self.iucn_id:
            return 'Unknown'
        return f'`{self.iucn_category_humanized}` [{self.iucn_id}]({self.iucn_url})'

    @property
    def description_lines(self):
        return [
            '|  |  |',
            '| --- | --- |',
            '| **Scientific Name** | ' + f'*{self.scientific_name_link}* ' +
            f'{self.authorship} |',
            f'| **Genus** | {self.genus_link} |',
            f'| **Family** | {self.family_link} |',
            f'| **Common Names** | {self.common_names_pretty} |',
            '| **Identification Confidence** | ' +
            f'{self.confidence_emoji} {self.confidence:.1%} |',
            f'| **Other Candidates** | {self.other_candidates_pretty} |',
            '|  |  |',

            f'| **Global Biodiversity Information Facility (GBIF)** | {self.gbif_pretty} |',
            f'| **Plants of the World Online (POWO)** | {self.powo_pretty} |',
            f'| **International Union for Conservation of Nature (IUCN)** | {self.iucn_pretty} |',

            '|  |  |',
            f'| **Time** | {self.time_str} |',
            f'| **Camera Direction** | {self.direction_pretty} |',
            f'| **Location** | {self.google_maps_link} |',
            f'| **Altitude** | {self.alt:.1f}m |',

        ]

    @classmethod
    def build_readme(cls):
        lines = ['# Plants for Sri Lanka :sri_lanka:', '']

        idx = cls.idx()
        for family, idx_family in idx.items():
            lines.extend([f'## {MetaDataREADME.get_wiki_link(family)}', ''])
            for genus, idx_genus in idx_family.items():
                lines.extend(
                    [f'### {MetaDataREADME.get_wiki_link(genus)}', ''])
                for species, md_list in idx_genus.items():
                    lines.extend(
                        [f'#### {MetaDataREADME.get_wiki_link(species)}', ''])

        File(MetaDataREADME.README_PATH).write_lines(lines)
        log.debug(f'Wrote {MetaDataREADME.README_PATH}')
