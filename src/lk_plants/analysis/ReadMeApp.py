from functools import cached_property

from lk_plants.analysis.InfoReadMe import InfoReadMe
from utils_future import Markdown, MarkdownPage


class ReadMeApp(MarkdownPage, InfoReadMe):
    @cached_property
    def file_path(self):
        return 'README.app.md'

    @cached_property
    def lines(self) -> list[str]:
        return [
            '## The '
            + Markdown.link('Plants', 'https://nuuuwan.github.io/plants')
            + ' App',
            '',
            'Results can be directly inspected using our '
            + Markdown.link('Plants', 'https://nuuuwan.github.io/plants')
            + " App.",
            '',
            Markdown.image('App', 'images/app.png'),
            '',
        ]
