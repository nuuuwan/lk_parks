from functools import cached_property

from utils import File, Log, Time, TimeFormat

from lk_plants.analysis.ConfusionReport import ConfusionReport
from lk_plants.analysis.IdentificationReport import IdentificationReport
from lk_plants.analysis.TaxonomyReport import TaxonomyReport
from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto
from utils_future import Markdown

log = Log('ViharamahadeviParkReport')


class ViharamahadeviParkReport(
    ConfusionReport, TaxonomyReport, IdentificationReport
):
    @staticmethod
    def is_vmd_park(data):
        BOUNDS = [
            [6.911, 79.857],
            [6.917, 79.866],
        ]
        latlng = data.latlng

        return (
            BOUNDS[0][0] <= latlng.lat <= BOUNDS[0][1]
            and BOUNDS[1][0] <= latlng.lng <= BOUNDS[1][1]
        )

    @cached_property
    def data_list(self):
        data_list = PlantPhoto.list_all()
        data_vmd_park_list = [
            data for data in data_list if self.is_vmd_park(data)
        ]
        return data_vmd_park_list

    @cached_property
    def n_plant_photos(self):
        return len(self.data_list)

    @cached_property
    def time_str(self):
        return TimeFormat('%b %d, %Y (%I:%M %p)').stringify(Time.now())

    @cached_property
    def lines_header(self):
        return [
            '# Plants of Vihaaramahadevi Park :sri_lanka:',
            '',
            '*This analysis was automatically '
            + f'generated on  **{self.time_str}**, '
            + f'and is based on  **{self.n_plant_photos}** plant photos.*',
            '',
            'Results can be directly inspected using '
            + Markdown.link('this app', 'https://nuuuwan.github.io/plants'),
            '',
            Markdown.image('App', 'image.app.png'),
            '',
        ]

    @cached_property
    def lines_background(self):
        return [
            '## Background',
            '',
            'Viharamahadevi Park (Sinhala: විහාරමහාදේවී උද්‍යානය; formerly Victoria Park, Sinhala: වික්ටෝරියා පාක්) is a public park located in Cinnamon Gardens, in [Colombo](https://en.wikipedia.org/wiki/Colombo), situated in front of the colonial-era Town Hall in Sri Lanka. It was built by the British colonial administration and is the oldest and largest park of Colombo. The park was originally named "Victoria Park" after Queen Victoria but was renamed after Queen Viharamahadevi, the mother of King Dutugamunu on July 18, 1958. [[Wikipedia](https://en.wikipedia.org/wiki/Viharamahadevi_Park)]',  # noqa
            '',
            'Viharamahadevi Park is 24.27ha, and has an estimated [green cover](https://en.wikipedia.org/wiki/Vegetation) of 14.39ha (59% from the total area). The estimated crown cover 12.25ha (50%). [[Madurapperum et al](https://www.researchgate.net/publication/282250239_CrownTree_cover_of_Viharamahadevi_Park_Colombo)]',  # noqa
            '',
        ]

    @cached_property
    def lines_analysis(self):
        return (
            [
                '## Summary Statistics',
                '',
            ]
            + self.lines_analysis_families
            + self.lines_analysis_genera
            + self.lines_analysis_species
            + self.lines_identification_score
        )

    @cached_property
    def lines(self):
        return (
            self.lines_header
            + self.lines_background
            + self.lines_analysis
            + self.lines_confusion
        )

    def write(self):
        path = 'README.md'
        File(path).write('\n'.join(self.lines))
        log.info(f'Wrote {path}')
