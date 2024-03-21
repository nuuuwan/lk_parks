from functools import cached_property

from utils import Log

from lk_plants.core.plant_net.PlantNetResult import PlantNetResult

log = Log('IdentificationReport')


class IdentificationReport:
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
            self.species_name_to_score_list.items(),
            key=lambda x: sum(x[1]) / len(x[1]),
            reverse=True,
        )
        return sorted_species_name_and_score_list

    @cached_property
    def lines_identification_score(self):
        MIN_PHOTOS = 5
        lines = [
            '## Identification Confidence '
            + f'(by Species with at least {MIN_PHOTOS} Photos)',
            '',
            '| Species | n(Photos) | Confidence (25th pctl.) '
            + '| Confidence (Median) | Confidence (75th pctl.) |',
            '|:---|---:|---:|---:|---:|',
        ]

        for species_name, scores in self.sorted_species_name_and_score_list:
            n = len(scores)
            if n < MIN_PHOTOS:
                continue

            i_low = int(n * 0.25)
            i_mid = int(n * 0.5)
            i_high = int(n * 0.75)
            sorted_scores = sorted(scores)
            low = sorted_scores[i_low]
            mid = sorted_scores[i_mid]
            high = sorted_scores[i_high]

            lines.append(
                f'| *{species_name}* | {n:,} | {low:.1%} '
                + f'| {mid:.1%} | {high:.1%} |'
            )
        lines.append('')
        return lines
