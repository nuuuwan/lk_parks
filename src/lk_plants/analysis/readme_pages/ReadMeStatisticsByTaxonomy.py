from functools import cache, cached_property

from utils import Log

from lk_plants.analysis.InfoReadMe import InfoReadMe
from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from lk_plants.core.taxonomy import RankClass
from lk_plants.core.taxonomy.Species import Species
from lk_plants.core.taxonomy.taxon import Taxon
from lk_plants.core.wiki import WikiPage
from utils_future import Markdown, MarkdownPage

log = Log('ReadMeStatisticsByTaxonomy')


class ReadMeStatisticsByTaxonomy(MarkdownPage, InfoReadMe):
    N_DISPLAY = 10

    @cache
    def get_rank_to_data_list(self, rank):
        key_to_data_list = {}
        for plant_photo in self.plant_photo_list:
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
            if not plant_net_result:
                continue
            species = Species.from_name(plant_net_result.top_species_name)
            rank_idx = species.rank_idx
            key = rank_idx[rank].name
            if key is None:
                continue

            if key not in key_to_data_list:
                key_to_data_list[key] = []
            key_to_data_list[key].append(plant_photo)
        return key_to_data_list

    def get_sorted_rank_and_data_list(self, get_key):
        key_to_data_list = self.get_rank_to_data_list(get_key)
        sorted_key_and_data_list = sorted(
            key_to_data_list.items(), key=lambda x: -len(x[1])
        )
        top_list = sorted_key_and_data_list[
            : ReadMeStatisticsByTaxonomy.N_DISPLAY
        ]
        others_list_list = sorted_key_and_data_list[
            ReadMeStatisticsByTaxonomy.N_DISPLAY:
        ]
        others_list = []
        for data_list in others_list_list:
            others_list.extend(data_list)
        top_list.append(('(All Others)', others_list))
        return top_list

    @cache
    def get_lines_analysis_by_rank_table(self, rank):
        LEN_DESCRIPTION = 400
        lines = Markdown.table(
            ['#', rank.title(), 'n(Photos)', '%', 'Description'],
            [
                Markdown.ALIGN_RIGHT,
                Markdown.ALIGN_LEFT,
                Markdown.ALIGN_RIGHT,
                Markdown.ALIGN_RIGHT,
                Markdown.ALIGN_LEFT,
            ],
        )

        for i, [key, data_list] in enumerate(
            self.get_sorted_rank_and_data_list(rank)
        ):
            n = len(data_list)
            p = n / self.n_plant_photos
            row_str = (
                (i + 1) if i < ReadMeStatisticsByTaxonomy.N_DISPLAY else ''
            )

            wiki_page_name = Taxon.get_wiki_page_name(key)
            description = ''
            if 'Others' not in key and 'Unknown-' not in key:
                description = WikiPage.from_wiki_page_name(
                    wiki_page_name
                ).get_summary_truncated(LEN_DESCRIPTION)

                if rank == 'species':
                    species = Species.from_name(key)
                    common_names = species.common_names
                    description = Markdown.bold(
                        'Common Names: '
                    ) + Markdown.italic(
                        ', '.join(common_names) + '. ' + description
                    )

            lines.extend(
                Markdown.table(
                    [
                        row_str,
                        Markdown.wiki_link(key),
                        f'{n:,}',
                        f'{p:.1%}',
                        description,
                    ],
                )
            )

        return lines

    @cache
    def get_lines_analysis_by_rank(self, rank):
        rank_to_data_list = self.get_rank_to_data_list(rank)
        n_unique = len(rank_to_data_list)
        label = rank.title()
        return (
            [
                f'### {label}',
                '',
                f'**{n_unique}** unique {label}(s).',
                '',
            ]
            + self.get_lines_analysis_by_rank_table(rank)
            + ['']
        )

    @cached_property
    def lines_analysis_families(self):
        return self.get_lines_analysis_by_rank('family')

    @cached_property
    def file_path(self):
        return 'README.statistics.taxonomy.md'

    @cached_property
    def lines_for_ranks(self):
        lines = []
        ranks = reversed(RankClass.list_all_keys()[2:])
        for rank in ranks:
            lines_for_rank = self.get_lines_analysis_by_rank(rank)
            lines.extend(lines_for_rank)
        return lines

    @cached_property
    def lines(self) -> list[str]:
        return [
            '## Statistics by Taxonomy',
            '',
        ] + self.lines_for_ranks
