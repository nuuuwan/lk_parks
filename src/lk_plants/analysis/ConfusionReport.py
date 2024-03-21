from functools import cached_property

from utils import Log

from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from utils_future import Markdown

log = Log('ConfusionReport')


class ConfusionReport:
    MIN_PHOTOS = 3

    @cached_property
    def confusion_key_to_n(self):
        key_to_n = {}
        for data in self.data_list:
            plant_net_result = PlantNetResult.from_plant_photo(data)
            species_name_to_score = plant_net_result.species_name_to_score
            species_names = list(species_name_to_score.keys())
            if len(species_names) < 2:
                continue
            species_name_1, species_name_2 = species_names[:2]
            score_1 = species_name_to_score[species_name_1]
            score_2 = species_name_to_score[species_name_2]
            if score_1 > 2 * score_2:
                continue
            if species_name_1 > species_name_2:
                species_name_1, species_name_2 = (
                    species_name_2,
                    species_name_1,
                )
            key = f'{species_name_1} & {species_name_2}'
            if key not in key_to_n:
                key_to_n[key] = 0
            key_to_n[key] += 1
        return key_to_n

    @cached_property
    def lines_confusion_table(self):
        lines = Markdown.table(
            ['Species 1', 'Species 2', 'n(Photos)'],
            [
                Markdown.ALIGN_LEFT,
                Markdown.ALIGN_LEFT,
                Markdown.ALIGN_RIGHT,
            ],
        )

        key_to_n = self.confusion_key_to_n
        for key, n in sorted(key_to_n.items(), key=lambda x: -x[1]):
            if n < ConfusionReport.MIN_PHOTOS:
                continue
            species_name_1, species_name_2 = key.split(' & ')
            lines.extend(
                Markdown.table(
                    [
                        Markdown.italic(species_name_1),
                        Markdown.italic(species_name_2),
                        f'{n:,}',
                    ],
                )
            )
        return lines

    @cached_property
    def lines_confusion(self):
        lines = [
            '## Pairs of Plant Species, likely confused '
            + 'during identification '
            + f'(at least {ConfusionReport.MIN_PHOTOS} times)',
            '',
        ]
        lines.extend(self.lines_confusion_table)

        lines.append('')
        return lines
