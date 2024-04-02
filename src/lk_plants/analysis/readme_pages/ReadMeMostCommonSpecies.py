import random
from functools import cached_property

from utils import Log

from lk_plants.analysis.readme_pages.ReadMeStatisticsByTaxonomy import \
    ReadMeStatisticsByTaxonomy
from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from lk_plants.core.taxonomy.Species import Species
from lk_plants.core.wiki.WikiPage import WikiPage
from utils_future import Markdown

log = Log('ReadMeMostCommonSpecies')


class ReadMeMostCommonSpecies(ReadMeStatisticsByTaxonomy):
    MAX_PLANT_PHOTOS = 3

    @staticmethod
    def get_image_all_md(species_name, best_plant_photos):
        image_md_list = []
        for plant_photo in best_plant_photos:
            image_path = plant_photo.image_path
            image_path_unix = image_path.replace('\\', '/')
            p_dim = 1.0 / ReadMeMostCommonSpecies.MAX_PLANT_PHOTOS - 0.01
            dim = f'{p_dim:.0%}'
            image_md = Markdown.image_html(
                species_name, image_path_unix, width=dim, height=dim
            )
            image_md_list.append(image_md)
        image_all_md = ' '.join(image_md_list)
        return image_all_md

    @staticmethod
    def get_lines_for_species(species_name, plant_photo_list):
        random.shuffle(plant_photo_list)
        best_plant_photos = plant_photo_list[
            : ReadMeMostCommonSpecies.MAX_PLANT_PHOTOS
        ]

        image_all_md = ReadMeMostCommonSpecies.get_image_all_md(
            species_name, best_plant_photos
        )

        plant_net_result = PlantNetResult.from_plant_photo(
            best_plant_photos[0]
        )
        species_name = plant_net_result.top_species_name
        species = Species.from_name(species_name)
        wiki_page_name = species.wiki_page_name
        wiki_page = WikiPage.from_wiki_page_name(wiki_page_name)
        summary = wiki_page.summary
        genus = species.genus
        family = genus.family

        common_names_str = ', '.join(species.common_names)

        n_photos = len(plant_photo_list)

        lines = [
            '### '
            + Markdown.wiki_link(species_name)
            + ' ('
            + Markdown.wiki_link(family.name)
            + ')',
            '',
            Markdown.italic(f'{n_photos} Photos'),
            '',
            image_all_md,
            '',
            Markdown.italic(common_names_str),
            '',
            summary
            + ' '
            + Markdown.ref(Markdown.wiki_link(wiki_page_name, 'Wikipedia')),
            '',
        ]
        return lines

    @cached_property
    def lines_most_common_species(self):
        key_and_data_list = self.get_sorted_key_and_data_list(
            ReadMeStatisticsByTaxonomy.get_key_species
        )
        lines = []
        for key, data_list in key_and_data_list[
            : ReadMeStatisticsByTaxonomy.N_DISPLAY
        ]:
            lines.extend(
                ReadMeMostCommonSpecies.get_lines_for_species(key, data_list)
            )
        return lines

    @cached_property
    def file_path(self):
        return 'README.most_common_species.md'

    @cached_property
    def lines(self) -> list[str]:
        random.seed(0)
        return [
            '## Most Common Species',
            '',
        ] + self.lines_most_common_species
