from dataclasses import dataclass


@dataclass
class LatLng:
    lat: float
    lng: float

    def to_dict(self) -> dict:
        return {
            'lat': self.lat,
            'lng': self.lng,
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            lat=d['lat'],
            lng=d['lng'],
        )


class Markdown:
    ALIGN_LEFT = ':---'
    ALIGN_RIGHT = '---:'
    # ALIGN_CENTER = ':---:'

    @staticmethod
    def italic(text):
        return f'*{text}*'

    # @staticmethod
    # def bold(text):
    #     return f'**{text}**'

    @staticmethod
    def link(text, url):
        return f'[{text}]({url})'

    @staticmethod
    def image(alt, url):
        return f'![{alt}]({url})'

    @staticmethod
    def table_row(cells):
        inner = ' | '.join([str(cell) for cell in cells])
        return f'| {inner} |'

    @staticmethod
    def table(*cells_list):
        first_cells = cells_list[0]
        for cells in cells_list[1:]:
            if len(cells) != len(first_cells):
                raise ValueError(
                    'All rows must have the same number of cells'
                )

        return '\n'.join([Markdown.table_row(cells) for cells in cells_list])
