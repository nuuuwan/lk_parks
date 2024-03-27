from functools import cached_property

from lk_plants.analysis.InfoReadMe import InfoReadMe
from utils_future import MarkdownPage


class ReadMeDuplicates(MarkdownPage, InfoReadMe):
    @cached_property
    def file_path(self):
        return 'README.duplicates.md'

    @cached_property
    def lines(self) -> list[str]:
        return [
            '## Duplicates',
            '',
        ]
