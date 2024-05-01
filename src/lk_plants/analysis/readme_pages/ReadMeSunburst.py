import os
from functools import cached_property

import plotly.express as px
import plotly.io as pio
from utils import Log

from lk_plants.analysis.InfoReadMe import InfoReadMe
from lk_plants.core import PlantNetResult, Species
from lk_plants.core.taxonomy import RankClass
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
        n_species = len(species_to_n)

        for i_species, [species_name, n] in enumerate(
            sorted(
                species_to_n.items(),
                key=lambda x: -x[1],
            )
        ):
            rank_idx = species_to_rank_idx[species_name]
            rank_to_name = {
                rank: rank_obj.name for rank, rank_obj in rank_idx.items()
            }
            p = 1 - i_species / n_species
            d_list.append(rank_to_name | dict(n=n) | dict(color=p))
        return d_list

    @cached_property
    def line_chart(self):
        fig = px.sunburst(
            self.d_list,
            path=RankClass.list_all_keys(),
            values="n",
            color="color",
            color_continuous_scale='Greens',
        )

        width = ReadMeSunburst.IMAGE_WIDTH
        fig.update_layout(
            autosize=False,
            coloraxis_showscale=False,
            width=width,
            height=width,
        )
        fig.update_coloraxes(showscale=False)

        image_path = os.path.join('images', 'sunburst.png')
        pio.write_image(fig, image_path, scale=5)
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
