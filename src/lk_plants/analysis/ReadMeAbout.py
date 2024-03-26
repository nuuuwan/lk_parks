from functools import cached_property

from lk_plants.analysis.InfoReadMe import InfoReadMe
from utils_future import MarkdownPage


class ReadMeAbout(MarkdownPage, InfoReadMe):
    @cached_property
    def file_path(self):
        return 'README.about.md'

    @cached_property
    def lines(self) -> list[str]:
        return [
            '## About this Project',
            '',
            'This analysis is part of a project to'+' identify plants in Sri Lanka\'s public parks.',
            '',
            'It was automatically '
            + f'generated on  **{self.time_str}**, '
            + f'and is based on  **{self.n_plant_photos}** plant photos.*',
            '',
        ]
