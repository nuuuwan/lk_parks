import os
from dataclasses import dataclass

from utils import File, Log

log = Log('MetaData')


@dataclass
class MetaDataREADME:
    README_PATH = os.path.join('README.md')

    @property
    def scientific_name_link(self) -> str:
        return f'[{self.scientific_name}]({self.wikipedia_url})'

    @property
    def title(self) -> str:
        return f'{self.confidence_emoji}'+f' {self.scientific_name_link} ({self.google_maps_link})'

    @property
    def google_maps_link(self) -> str:
        lat, lng = self.latlng
        url = f'https://www.google.com/maps/place/{lat}N,{lng}E'
        label = f'{lat:.4f}°N,{lng:.4f}°E'
        return f'[{label}]({url})'

    @property
    def description_lines(self):
        return [
            '|  |  |',
            '| --- | --- |',
            f'| **Scientific Name** | *{self.scientific_name_link}* |',
            f'| **Genus** | {self.genus} |',
            f'| **Family** | {self.family} |',
            f'| **Common Names** | {", ".join(self.common_names)} |',
            f'| **Confidence** | '+f'{self.confidence_emoji} {self.confidence:.1%} |',
            f'| **Other Candidates** | {self.other_candidates_pretty} |',
            '|  |  |',
            f'| **Time** | {self.time_str} |',
            f'| **Location** | {self.google_maps_link} |',
            f'| **Altitude** | {self.alt:.1f}m |',
            f'| **Camera Direction** | {self.direction_pretty} |',
        ]

    # README
    @classmethod
    def lines_summary(cls):
        summary = cls.summary()
        n = summary['n']
        n_families = len(summary['family_to_n'])
        n_genera = len(summary['genus_to_n'])
        n_species = len(summary['species_to_n'])
        lines = [
            '## Summary Statistics',
            '',
            '|  |  |',
            '| --- | ---: |',
            f'| **Total Plants** | {n} |',
            f'| **Unique Families** | {n_families} |',
            f'| **Unique Genera** | {n_genera} |',
            f'| **Unique Species** | {n_species} |',
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
