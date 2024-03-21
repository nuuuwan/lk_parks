import os
from functools import cached_property

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from utils import Log

from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from utils_future import Markdown

log = Log('IdentificationReport')


class IdentificationReport:
    MIN_PHOTOS = 10

    @staticmethod
    def get_short_species_name(x):
        words = x.split(' ')
        return words[0][0] + '. ' + words[1]

    @cached_property
    def sorted_species_name_and_score_list(self):
        species_name_to_score_list = {}
        for data in self.data_list:
            plant_net_result = PlantNetResult.from_plant_photo(data)
            species_name_to_score = plant_net_result.species_name_to_score
            if not species_name_to_score:
                continue
            species_name = list(species_name_to_score.keys())[0]
            score = species_name_to_score[species_name]
            if species_name not in species_name_to_score_list:
                species_name_to_score_list[species_name] = []
            species_name_to_score_list[species_name].append(score)

        sorted_species_name_and_score_list = sorted(
            species_name_to_score_list.items(),
            key=lambda x: sum(x[1]) / len(x[1]),
        )

        return sorted_species_name_and_score_list

    @cached_property
    def indentification_score_data(self):
        COLORS = ['#f008', '#f808', '#0808']
        n_colors = len(COLORS)
        x = []
        y = []
        colors = []
        for species_name, scores in self.sorted_species_name_and_score_list:
            n = len(scores)
            if n < IdentificationReport.MIN_PHOTOS:
                continue
            for i, score in enumerate(sorted(scores)):
                i_color = int(n_colors * i / n)
                color = COLORS[i_color]
                species_name_short = self.get_short_species_name(species_name)
                x.append(species_name_short)
                y.append(score)
                colors.append(color)
        return x, y, colors

    @cached_property
    def lines_identification_score_chart(self):
        x, y, colors = self.indentification_score_data

        plt.scatter(y, x, color=colors)
        title = ''

        plt.title(
            'Identification Confidence - By Species '
            + f'(≥{IdentificationReport.MIN_PHOTOS} photos)'
        )
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        plt.tight_layout()

        chart_image_path = os.path.join(
            'images', 'identification_score.species.png'
        )
        plt.savefig(chart_image_path)
        log.info(f'Wrote {chart_image_path}')

        chart_image_path_unix = chart_image_path.replace('\\', '/')
        return [Markdown.image(title, chart_image_path_unix)]

    @cached_property
    def lines_identification_score(self):
        lines = [
            '## Identification Confidence',
            '',
        ]

        lines.extend(self.lines_identification_score_chart)
        lines.append('')
        return lines
