from functools import cached_property

from utils import File, Log

log = Log('MarkdownPage')


class MarkdownPage:
    @cached_property
    def child_pages(self) -> list['MarkdownPage']:
        return []

    @cached_property
    def lines(self) -> list[str]:
        raise NotImplementedError()

    @cached_property
    def file_path(self) -> str:
        raise NotImplementedError()

    def write(self):
        lines = self.lines
        for child_page in self.child_pages:
            lines.extend(child_page.lines)
        content = '\n'.join(lines)
        File(self.file_path).write(content)
        log.info(f'Wrote {self.file_path}')
