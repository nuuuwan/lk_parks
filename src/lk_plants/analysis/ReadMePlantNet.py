from functools import cached_property

from lk_plants.analysis.InfoReadMe import InfoReadMe
from utils_future import Markdown, MarkdownPage


class ReadMePlantNet(MarkdownPage, InfoReadMe):
    @cached_property
    def file_path(self):
        return 'README.plant_net.md'

    @cached_property
    def lines(self) -> list[str]:
        return [
            '## ' + Markdown.link('PlantNet', 'https://plantnet.org'),
            '',
            Markdown.image(
                'PlantNet',
                'https://plantnet.org'
                + '/wp-content/uploads/2020/12/plantnet_header.png',
            ),
            '',
            "Plant Identifications are from  "
            + Markdown.link('PlantNet', 'https://plantnet.org')
            + ", a citizen science project for automatic plant identification "
            + "through photographs and based on machine learning.",
            "",
            Markdown.italic(
                "We only consider results where the model's "
                + "identification confidence is "
                + Markdown.bold(f"≥ {InfoReadMe.MIN_CONFIDENCE:.0%}.")
            ),
            '',
        ]
