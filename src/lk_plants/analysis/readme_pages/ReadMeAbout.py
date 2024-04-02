from functools import cached_property

from lk_plants.analysis.InfoReadMe import InfoReadMe
from utils_future import MarkdownPage, Markdown


class ReadMeAbout(MarkdownPage, InfoReadMe):
    @cached_property
    def file_path(self):
        return 'README.about.md'

    @cached_property
    def lines(self) -> list[str]:
        return [
            '## About',
            '',
            'This project aims to use '
            + 'Computer Vision and Artificial Intelligence'
            + ' to identify plants in Sri Lanka\'s public parks, '
            + 'beginning with Viharamahadevi Park, Colombo.',
            '',
            '🤖 *This report was automatically '
            + f'generated on  **{self.time_str}**, '
            + f'and is based on **{self.n_plant_photos}** plant photos.*',
            '',
            'You can also follow us on our Twitter/X page ' + Markdown.link(
                '@lk_plants',
                'https://twitter.com/lk_plants',
            ), 
            '',
        ]
