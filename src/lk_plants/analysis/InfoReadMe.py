from functools import cached_property

from utils import Log, Time, TimeFormat

from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto

log = Log('InfoReadMe')


class InfoReadMe:
    MIN_CONFIDENCE = 0.2

    @staticmethod
    def should_analyze(plant_photo):
        BOUNDS = [
            [6.911, 79.857],
            [6.917, 79.866],
        ]
        latlng = plant_photo.latlng

        if not (
            BOUNDS[0][0] <= latlng.lat <= BOUNDS[0][1]
            and BOUNDS[1][0] <= latlng.lng <= BOUNDS[1][1]
        ):
            return False

        plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
        species_name_to_score = plant_net_result.species_name_to_score
        if not species_name_to_score:
            return False

        species_name, score = list(species_name_to_score.items())[0]
        if score < InfoReadMe.MIN_CONFIDENCE:
            return False
        return True

    @cached_property
    def data_list(self):
        data_list = PlantPhoto.list_all()
        data_vmd_park_list = [
            data for data in data_list if self.should_analyze(data)
        ]
        return data_vmd_park_list

    @cached_property
    def n_plant_photos(self):
        return len(self.data_list)

    @cached_property
    def time_str(self):
        return TimeFormat('%b %d, %Y (%I:%M %p)').stringify(Time.now())
