from functools import cached_property

from lk_plants.analysis.InfoReadMe import InfoReadMe
from lk_plants.analysis.readme_pages import (ReadMeAbout, ReadMeApp,
                                             ReadMeDifficultIds,
                                             ReadMeDuplicates, ReadMeFunnel,
                                             ReadMeIdentification,
                                             ReadMeMostCommonSpecies,
                                             ReadMePlantNet,
                                             ReadMeStatisticsByTaxonomy,
                                             ReadMeVMDPark)
from utils_future import MarkdownPage


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
            ReadMeDuplicates(),
            ReadMeIdentification(),
        ]
