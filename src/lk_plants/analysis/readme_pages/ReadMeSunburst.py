import os
import random
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

    @cached_property
    def d_list(self):
        species_to_rank_idx = {}
        species_to_n = {}
        for plant_photo in self.plant_photo_list:
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
            if not plant_net_result:
                continue
            top_species_name = plant_net_result.top_species_name
            if not top_species_name:
                continue
            species = Species.from_name(top_species_name)
            species_name = species.name
            if species_name not in species_to_n:
                species_to_rank_idx[species_name] = species.rank_idx
                species_to_n[species_name] = 0
            species_to_n[species_name] += 1

        d_list = []
        for species_name, n in sorted(
            species_to_n.items(),
            key=lambda x: -x[1],
        ):
            rank_idx = species_to_rank_idx[species_name]
            d_list.append(rank_idx | dict(n=n) | dict(color="red"))
        return d_list

    @staticmethod
    def get_color_sequence():
        sequence = []

        for s in [100]:
            for l in range(20, 35, 5):
                for h in range(0, 150, 10):
                    color = f'hsl({h},{s}%,{l}%)'
                    sequence.append(color)
        random.shuffle(sequence)
        return sequence

    @cached_property
    def line_chart(self):
        d_list = self.d_list

        rank_type_list = [
            'domain',
            'kingdom',
            'phylum',
            'classis',
            'order',
            'family',
            'genus',
            'species',
        ]

        names = []
        parents = []
        values = []
        colors = []

        color_rank_type = "genus"

        for i, rank_type in enumerate(rank_type_list[1:], start=1):
            parent_rank_type = rank_type_list[i - 1]

            name_to_n = {}
            name_to_parent = {}
            name_to_color = {}
            for d in d_list:
                name = d[rank_type]
                if name not in name_to_n:
                    name_to_n[name] = 0
                    name_to_parent[name] = d[parent_rank_type]
                    name_to_color[name] = d[color_rank_type]
                name_to_n[name] += d['n']

            for name, n in sorted(name_to_n.items(), key=lambda x: -x[1]):
                names.append(name)
                parents.append(name_to_parent[name])
                values.append(n)
                colors.append(name_to_color[name])

        data = dict(
            names=names,
            parents=parents,
            values=values,
            colors=colors,
        )

        fig = px.sunburst(
            data,
            names="names",
            parents="parents",
            values="values",
            color="colors",
            branchvalues='total',
            color_discrete_sequence=ReadMeSunburst.get_color_sequence(),
        )

        width = ReadMeSunburst.IMAGE_WIDTH
        fig.update_layout(autosize=False, width=width, height=width)

        image_path = os.path.join('images', 'sunburst.png')
        pio.write_image(fig, image_path, scale=3)
        log.info(f'Wrote {image_path}')
        os.startfile(image_path)

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
