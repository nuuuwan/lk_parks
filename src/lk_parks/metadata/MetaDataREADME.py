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

    @property
    def common_names_pretty(self) -> str:
        if not self.common_names:
            return '-'
        return ', '.join(self.common_names)

    @property
    def scientific_name_link(self) -> str:
        wiki_url = self.get_wiki_url(self.scientific_name)
        return f'[{self.scientific_name}]({wiki_url})'


    @property
    def family_link(self) -> str:
        wiki_url = self.get_wiki_url(self.family)
        return f'[{self.family}]({wiki_url})'
    
    @property
    def genus_link(self) -> str:
        wiki_url = self.get_wiki_url(self.genus)
        return f'[{self.genus}]({wiki_url})'

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

            f'| **GBIF** | {self.gbif_pretty} |',
            f'| **POWO** | {self.powo_pretty} |',
            f'| **IUCN** | {self.iucn_pretty} |',

            '|  |  |',
            f'| **Time** | {self.time_str} |',
            f'| **Camera Direction** | {self.direction_pretty} |',
            f'| **Location** | {self.google_maps_link} |',
            f'| **Altitude** | {self.alt:.1f}m |',

        ]

    # README
    @classmethod
    def lines_summary(cls):
        summary = cls.summary()
        n = summary['n']
        n_families = len(summary['family_to_n'])
        n_genera = len(summary['genus_to_n'])
        n_species = len(summary['species_to_n'])

        def common(key_to_n):
            N_DISPLAY = 5
            lines = [
                f'{key} ({n})' for key,
                n in list(
                    key_to_n.items())[
                    :N_DISPLAY]]
            return ', '.join(
                lines)

        common_families = common(summary['family_to_n'])
        common_genera = common(summary['genus_to_n'])
        common_species = common(summary['species_to_n'])

        lines = [
            '## Summary Statistics',
            '',
            '|  |  |  |',
            '| --- | ---: | --- |',
            f'| **Unique Families** | {n_families} | {common_families} |',
            f'| **Unique Genera** | {n_genera} | {common_genera} |',
            f'| **Unique Species** | {n_species} | {common_species} |',
            f'| **Total Plants** | {n} | |',

        ]
        return lines

    @classmethod
    def build_readme(cls):
        lines = ['# Viharamahadevi Park, Colombo, Sri Lanka', '']
        lines.extend(cls.lines_summary())
        for md in cls.list_all():
            lines.append(f'## {md.title}')
            lines.append('')
            lines.append(f'![{md.image_path_unix}]({md.image_path_unix})')
            lines.append('')
            lines.extend(md.description_lines)
            lines.append('')
        File(MetaDataREADME.README_PATH).write_lines(lines)
        log.debug(f'Wrote {MetaDataREADME.README_PATH}')
