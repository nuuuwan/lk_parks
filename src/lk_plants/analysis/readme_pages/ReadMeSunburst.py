import os
import random
from functools import cached_property

import pandas
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
    def df(self):
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
            key=lambda x: x[1],
        ):
            rank_idx = species_to_rank_idx[species_name]
            d_list.append(rank_idx | dict(n=n) | dict(color="red"))
        return pandas.DataFrame(d_list)

    @staticmethod
    def get_color_sequence():
        sequence = []

        for h in range(0, 150, 5):
            color = f'hsl({h},100%,30%)'
            sequence.append(color)
        random.shuffle(sequence)
        return sequence

    @cached_property
    def line_chart(self):
        df = self.df

        fig = px.sunburst(
            df,
            path=[
                'domain',
                'kingdom',
                'phylum',
                'classis',
                'order',
                'family',
                'genus',
                'species',
            ],
            values='n',
            color="order",
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
