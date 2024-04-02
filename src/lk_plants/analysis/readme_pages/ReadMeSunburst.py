import os
from functools import cached_property

import plotly.express as px
import plotly.io as pio
from utils import Log

from lk_plants.analysis.InfoReadMe import InfoReadMe
from lk_plants.core import PlantNetResult, Species
from utils_future import Markdown, MarkdownPage

log = Log('ReadMeSunburst')


class ReadMeSunburst(MarkdownPage, InfoReadMe):
    IMAGE_WIDTH = 1000

    @cached_property
    def file_path(self):
        return 'README.sunburst.md'

    def get_data(self):
        plant_photos = self.plant_photo_list
        species_name_to_info = {}
        taxon_to_n = {}

        n_total = 0
        for plant_photo in plant_photos:
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
            if not plant_net_result:
                continue
            top_species_name = plant_net_result.top_species_name
            if not top_species_name:
                continue
            species = Species.from_name(top_species_name)
            species_name = species.name
            genus_name = species.genus.name
            family_name = species.genus.family.name

            n_total += 1
            if species_name not in species_name_to_info:
                species_name_to_info[species_name] = [genus_name, family_name]

            if species_name not in taxon_to_n:
                taxon_to_n[species_name] = 0
            taxon_to_n[species_name] += 1

            if family_name not in taxon_to_n:
                taxon_to_n[family_name] = 0
            taxon_to_n[family_name] += 1

            if genus_name not in taxon_to_n:
                taxon_to_n[genus_name] = 0
            taxon_to_n[genus_name] += 1

        categories = []
        parents = []
        values = []

        ROOT_CATEGORY_NAME = 'Plants'
        categories.append(ROOT_CATEGORY_NAME)
        parents.append('')
        values.append(n_total)

        parse_set = set()
        for species_name, info in species_name_to_info.items():
            [genus_name, family_name] = info
            if family_name in parse_set:
                continue
            parse_set.add(family_name)
            categories.append(family_name)
            parents.append(ROOT_CATEGORY_NAME)
            values.append(taxon_to_n[family_name])

        for species_name, info in species_name_to_info.items():
            [genus_name, family_name] = info
            if genus_name in parse_set:
                continue
            parse_set.add(genus_name)
            categories.append(genus_name)
            parents.append(family_name)
            values.append(taxon_to_n[genus_name])

        for species_name, info in species_name_to_info.items():
            [genus_name, family_name] = info
            categories.append(species_name)
            parents.append(genus_name)
            values.append(taxon_to_n[species_name])

        data = dict(
            categories=categories,
            parent=parents,
            value=values,
        )
        return data

    @cached_property
    def line_chart(self):
        data = self.get_data()
        fig = px.sunburst(
            data,
            names='categories',
            parents='parent',
            values='value',
            color_discrete_sequence=['#800', '#f80', '#fc0', '#080'],
            branchvalues='total',
        )

        width = ReadMeSunburst.IMAGE_WIDTH
        fig.update_layout(autosize=False, width=width, height=width)

        image_path = os.path.join('images', 'sunburst.png')
        pio.write_image(fig, image_path, scale=3)
        log.info(f'Wrote {image_path}')

        return Markdown.image(image_path, image_path)

    @cached_property
    def lines(self) -> list[str]:
        return [
            '## Overview of Taxonomies',
            '',
            'This sunburst chart shows the distribution of plant photos,'
            + ' by family, genus and species, weighted by number of trees.',
            '',
            self.line_chart,
            '',
        ]
