from functools import cache, cached_property

from utils import Log

from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from lk_plants.core.taxonomy.Species import Species
from utils_future import Markdown

log = Log('TaxonomyReport')


class TaxonomyReport:
    N_DISPLAY = 10

    @cache
    def get_key_to_data_list(self, get_key):
        key_to_data_list = {}
        for data in self.data_list:
            key = get_key(data)
            if key is None:
                continue
            if key not in key_to_data_list:
                key_to_data_list[key] = []
            key_to_data_list[key].append(data)
        return key_to_data_list

    def get_sorted_key_and_data_list(self, get_key):
        key_to_data_list = self.get_key_to_data_list(get_key)
        sorted_key_and_data_list = sorted(
            key_to_data_list.items(), key=lambda x: -len(x[1])
        )
        top_list = sorted_key_and_data_list[: TaxonomyReport.N_DISPLAY]
        others_list_list = sorted_key_and_data_list[
            TaxonomyReport.N_DISPLAY:
        ]
        others_list = []
        for data_list in others_list_list:
            others_list.extend(data_list)
        top_list.append(('(All Others)', others_list))
        return top_list

    @cache
    def get_lines_analysis_by_key_table(self, label, get_key):
        lines = Markdown.table(
            ['#', label, 'n(Photos)', '%'],
            [
                Markdown.ALIGN_RIGHT,
                Markdown.ALIGN_LEFT,
                Markdown.ALIGN_RIGHT,
                Markdown.ALIGN_RIGHT,
            ],
        )

        for i, [key, data_list] in enumerate(
            self.get_sorted_key_and_data_list(get_key)
        ):
            n = len(data_list)
            p = n / self.n_plant_photos
            row_str = (i + 1) if i < TaxonomyReport.N_DISPLAY else ''

            lines.extend(
                Markdown.table(
                    [row_str, Markdown.italic(key), f'{n:,}', f'{p:.1%}'],
                )
            )

        return lines

    @cache
    def get_lines_analysis_by_key(self, label, get_key):
        key_to_data_list = self.get_key_to_data_list(get_key)
        n_unique = len(key_to_data_list)
        return (
            [
                f'### {label}',
                '',
                f'**{n_unique}** unique {label}.',
                '',
            ]
            + self.get_lines_analysis_by_key_table(label, get_key)
            + ['']
        )

    @cached_property
    def lines_analysis_families(self):
        def get_key(plant_photo):
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
            species_name_to_score = plant_net_result.species_name_to_score
            if not species_name_to_score:
                return None
            species_name = list(species_name_to_score.keys())[0]
            species = Species.from_name(species_name)
            return species.genus.family.name

        return self.get_lines_analysis_by_key('Families', get_key)

    @cached_property
    def lines_analysis_genera(self):
        def get_key(plant_photo):
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
            species_name_to_score = plant_net_result.species_name_to_score
            if not species_name_to_score:
                return None
            species_name = list(species_name_to_score.keys())[0]
            species = Species.from_name(species_name)
            return species.genus.name

        return self.get_lines_analysis_by_key('Genera', get_key)

    @cached_property
    def lines_analysis_species(self):
        def get_key(plant_photo):
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
            species_name_to_score = plant_net_result.species_name_to_score
            if not species_name_to_score:
                return None
            species_name = list(species_name_to_score.keys())[0]
            return species_name

        return self.get_lines_analysis_by_key('Species', get_key)
