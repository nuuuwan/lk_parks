import os
from dataclasses import dataclass

from utils import File, Log

log = Log('MetaData')


@dataclass
class MetaDataREADME:
    README_PATH = os.path.join('README.md')

    @property
    def title(self) -> str:
        return f'🌳 {self.google_maps_link} ({self.time_str})'

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
            f'| **Time** | {self.time_str} |',
            f'| **Location** | {self.google_maps_link} |',
            f'| **Altitude** | {self.alt:.1f}m |',
            f'| **Camera Direction** | {self.direction_pretty} |',
        ]
    # README

    @classmethod
    def build_readme(cls):
        lines = ['# Viharamahadevi Park, Colombo, Sri Lanka', '']
        for md in cls.list_all():
            lines.append(f'## {md.title}')
            lines.append('')
            lines.extend(md.description_lines)
            lines.append('')
            lines.append(f'![{md.image_path_unix}]({md.image_path_unix})')
            lines.append('')
        File(MetaDataREADME.README_PATH).write_lines(lines)
        log.debug(f'Wrote {MetaDataREADME.README_PATH}')
