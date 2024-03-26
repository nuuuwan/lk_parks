from functools import cached_property

from lk_plants.analysis.InfoReadMe import InfoReadMe
from lk_plants.analysis.ReadMeAbout import ReadMeAbout
from lk_plants.analysis.ReadMeApp import ReadMeApp
from lk_plants.analysis.ReadMeDifficultIds import ReadMeDifficultIds
from lk_plants.analysis.ReadMeMostCommonSpecies import ReadMeMostCommonSpecies
from lk_plants.analysis.ReadMePlantNet import ReadMePlantNet
from lk_plants.analysis.ReadMeStatisticsByTaxonomy import \
    ReadMeStatisticsByTaxonomy
from lk_plants.analysis.ReadMeVMDPark import ReadMeVMDPark
from utils_future import MarkdownPage
from lk_plants.analysis.ReadMeFunnel import ReadMeFunnel


class ReadMe(MarkdownPage, InfoReadMe):
    @cached_property
    def file_path(self):
        return 'README.md'

    @cached_property
    def lines(self) -> list[str]:
        return [
            '# Plants of Sri Lanka :sri_lanka:',
            '',
        ]

    @cached_property
    def child_pages(self) -> list['MarkdownPage']:
        return [
            ReadMeAbout(),
            ReadMePlantNet(),
            ReadMeApp(),
            ReadMeVMDPark(),
            ReadMeFunnel(),
            ReadMeMostCommonSpecies(),
            ReadMeStatisticsByTaxonomy(),
            ReadMeDifficultIds(),
        ]
