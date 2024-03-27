from functools import cached_property

from utils import Log, Time, TimeFormat

from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto

log = Log('InfoReadMe')


class InfoReadMe:
    MIN_CONFIDENCE = 0.2

    @staticmethod
    def is_in_geo(plant_photo):
        BOUNDS = [
            [6.911, 79.857],
            [6.917, 79.866],
        ]
        latlng = plant_photo.latlng

        return (
            BOUNDS[0][0] <= latlng.lat <= BOUNDS[0][1]
            and BOUNDS[1][0] <= latlng.lng <= BOUNDS[1][1]
        )

    @staticmethod
    def has_conf(plant_photo, conf):
        plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
        score = plant_net_result.top_score
        return score and score >= conf

    @staticmethod
    def dedupe(plant_photo_list: list[PlantPhoto]):
        idx = {}
        for plant_photo in plant_photo_list:
            key = str(plant_photo.latlng)
            idx[key] = plant_photo
        return list(idx.values())

    @cached_property
    def plant_photo_list(self):
        raw = [plant_photo for plant_photo in PlantPhoto.list_all()]
        in_geo = [
            plant_photo for plant_photo in raw if self.is_in_geo(plant_photo)
        ]
        deduped = InfoReadMe.dedupe(in_geo)
        conf20 = [
            plant_photo
            for plant_photo in deduped
            if self.has_conf(plant_photo, 0.2)
        ]
        return conf20

    @cached_property
    def n_plant_photos(self):
        return len(self.plant_photo_list)

    @cached_property
    def time_str(self):
        return TimeFormat('%b %d, %Y (%I:%M %p)').stringify(Time.now())

    @cached_property
    def funnel(self) -> dict:
        raw = [plant_photo for plant_photo in PlantPhoto.list_all()]
        in_geo = [
            plant_photo for plant_photo in raw if self.is_in_geo(plant_photo)
        ]
        deduped = InfoReadMe.dedupe(in_geo)

        def get_conf(min_conf):
            return [
                plant_photo
                for plant_photo in deduped
                if self.has_conf(plant_photo, min_conf)
            ]

        pct5_or_more = get_conf(0.05)
        pct10_or_more = get_conf(0.1)
        pct20_or_more = get_conf(0.2)

        return {
            "All": len(raw),
            "In Geo": len(in_geo),
            "Deduped": len(deduped),
            "≥ 5%": len(pct5_or_more),
            "≥ 10%": len(pct10_or_more),
            "≥ 20%": len(pct20_or_more),
        }
