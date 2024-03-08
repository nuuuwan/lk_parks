import os
from dataclasses import dataclass

from utils import File, Log

from lk_parks.NameTranslator import NameTranslator

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
        return f'[`{x}`]({MetaDataREADME.get_wiki_url(x)})'

    @property
    def common_names_pretty(self) -> str:
        if not self.common_names:
            return '-'
        return ', '.join(self.common_names)

    @staticmethod
    def dot_join(*args):
        return ' · '.join(args)

    @property
    def title(self) -> str:
        return MetaDataREADME.dot_join(
            self.time_str,
            self.google_maps_link,
        )

    @property
    def google_maps_link(self) -> str:
        lat, lng = self.latlng
        url = f'https://www.google.com/maps/place/{lat}N,{lng}E'
        label = f'{lat:.4f}°N,{lng:.4f}°E'
        return f'[{label}]({url})'

    @property
    def gbif_pretty(self) -> str:
        if not self.gbif_id:
            return '(No Data)'
        return f'[{self.gbif_id}]({self.gbif_url})'

    @property
    def powo_pretty(self) -> str:
        if not self.powo_id:
            return '(No Data)'
        return f'[{self.powo_id}]({self.powo_url})'

    @property
    def iucn_pretty(self) -> str:
        if not self.iucn_id:
            return '(No Data)'
        return MetaDataREADME.dot_join(
            self.iucn_category_humanized,
            f'[{self.iucn_id}]({self.iucn_url})'
        )

    @property
    def image_md(self) -> str:
        return f'![{self.image_path_unix}]({self.image_path_unix})'

    @property
    def pretty_name_translations(self):
        nt = NameTranslator()
        data = nt.get(self.scientific_name)
        if not data:
            return ''
        parts = []
        if data['sinhala']:
            parts.append(f'`සි`: *{data["sinhala"]}*')
        if data['tamil']:
            parts.append(f'`த`: *{data["tamil"]}*')
        return MetaDataREADME.dot_join(*parts)

    @property
    def species_lines(self):
        return [
            f'*{self.common_names_pretty}*',
            '',
            f'{self.pretty_name_translations}',
            '',
            '|  |  |',

            '| --- | --- |',

            # '| **Scientific Name** | ' + f'*{MetaDataREADME.get_wiki_link(self.scientific_name)}* ' +
            # f'{self.authorship} |',
            # f'| **Genus** | {MetaDataREADME.get_wiki_link(self.genus)} |',
            # f'| **Family** | {MetaDataREADME.get_wiki_link(self.family)} |',
            f'| **Global Biodiversity Information Facility (GBIF)** | {self.gbif_pretty} |',
            f'| **Plants of the World Online (POWO)** | {self.powo_pretty} |',
            f'| **International Union for Conservation of Nature (IUCN)** | {self.iucn_pretty} |',
            '',

        ]

    @property
    def other_candidates_pretty(self) -> str:
        def format_item(item):
            species, score = item
            species_link = MetaDataREADME.get_wiki_link(species)
            return f'{species_link} ({score:.1%})'
        return ', '.join([format_item(x)
                         for x in self.species_to_score.items()])

    @property
    def confidence_combined(self) -> str:
        return f'*{self.confidence_emoji} ' + \
            f'Identification Confidence: {self.other_candidates_pretty}*'

    @property
    def photo_lines(self):
        return [
            f'#### {self.title}',
            '',
            self.confidence_combined,
            '',
            self.image_md,

            # '|  |  |',
            # '| --- | --- |',
            # '| **Identification Confidence** | ' +
            # f'{self.confidence_emoji} {self.confidence:.1%} |',
            # f'| **Other Guesses** | {self.other_candidates_pretty} |',
            # f'| **Time** | {self.time_str} |',
            # f'| **Camera Direction** | {self.direction_pretty} |',
            # f'| **Location** | {self.google_maps_link} |',
            # f'| **Altitude** | {self.alt:.1f}m |',

        ]

    @classmethod
    def build_readme(cls):
        lines = []

        idx = cls.idx()
        for family, idx_family in idx.items():
            lines.extend([f'# {MetaDataREADME.get_wiki_link(family)}', ''])
            for genus, idx_genus in idx_family.items():
                lines.extend(
                    [f'## {MetaDataREADME.get_wiki_link(genus)}', ''])
                for __, md_list in idx_genus.items():
                    n = len(md_list)
                    n_str = f'({n} Examples)' if n > 1 else '(1 Example)'
                    md0 = md_list[0]
                    lines.extend(
                        [f'### ' + f'*{MetaDataREADME.get_wiki_link(md0.scientific_name)}* ' + f'{md0.authorship}', ''])
                    lines.extend(md0.species_lines)
                    lines.extend([n_str, ''])
                    for md in md_list:
                        lines.extend(md.photo_lines)
                        lines.append('')

        File(MetaDataREADME.README_PATH).write_lines(lines)
        log.debug(f'Wrote {MetaDataREADME.README_PATH}')
