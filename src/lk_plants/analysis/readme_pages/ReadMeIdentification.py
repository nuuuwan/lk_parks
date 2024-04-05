from functools import cached_property

from utils import Log, Time, TimeFormat

from lk_plants.analysis.InfoReadMe import InfoReadMe
from lk_plants.analysis.readme_pages.ReadMeIdentificationCommon import (
    ReadMeIdentificationCommon,
)
from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from lk_plants.core.taxonomy.Species import Species
from utils_future import MarkdownPage

log = Log('ReadMeIdentification')


class ReadMeIdentification(
    MarkdownPage, InfoReadMe, ReadMeIdentificationCommon
):
    @cached_property
    def file_path(self):
        return 'README.identification.md'

    @cached_property
    def lines_direction(self):
        def get_key(plant_photo):
            if plant_photo.direction is None:
                return 0
            Q = 22.5
            return round(plant_photo.direction / Q) * Q

        return self.get_lines_for_key('camera direction', get_key)

    @cached_property
    def lines_time_only(self):
        def get_key(plant_photo):
            Q = 10 * 60
            ut = round(plant_photo.ut / Q) * Q
            time_only_str = TimeFormat('%H:%M').stringify(Time(ut))
            return time_only_str

        return self.get_lines_for_key('time of day', get_key)

    @cached_property
    def lines_date(self):
        def get_key(plant_photo):
            return TimeFormat('%m-%d').stringify(Time(plant_photo.ut))

        return self.get_lines_for_key('date', get_key)

    @cached_property
    def lines_latlng(self):
        def get_key(plant_photo):
            lat, lng = plant_photo.latlng.tuple
            return f'{lat:.3f},{lng:.3f}'

        return self.get_lines_for_key('latlng', get_key)

    @cached_property
    def lines_by_species(self):
        def get_key(plant_photo):
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
            species_name = plant_net_result.top_species_name
            if not species_name:
                return 'Unknown'
            genus, species_only = species_name.split(' ')
            return genus[:1] + '. ' + species_only[:5] + '.'

        return self.get_lines_for_key('species', get_key)

    @cached_property
    def lines_by_family(self):
        def get_key(plant_photo):
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
            species_name = plant_net_result.top_species_name
            if not species_name:
                return 'Unknown'
            species = Species.from_name(species_name)
            return species.genus.family.name[:5] + '.'

        return self.get_lines_for_key('family', get_key)

    @cached_property
    def lines(self) -> list[str]:
        return (
            [
                '## Identification Confidence',
                '',
            ]
            + self.lines_time_only
            + self.lines_date
            + self.lines_direction
            + self.lines_by_species
            + self.lines_by_family
            + self.lines_latlng
            + ['']
        )
