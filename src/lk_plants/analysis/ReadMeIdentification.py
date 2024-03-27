import os
from functools import cached_property

import matplotlib.pyplot as plt
from utils import Log, Time, TimeFormat

from lk_plants.analysis.InfoReadMe import InfoReadMe
from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto
from lk_plants.core.taxonomy.Species import Species
from utils_future import Markdown, MarkdownPage

log = Log('ReadMeIdentification')


class ReadMeIdentification(MarkdownPage, InfoReadMe):
    @cached_property
    def file_path(self):
        return 'README.identification.md'

    @staticmethod
    def get_analysis_by_key(get_key):
        plant_photo_list = PlantPhoto.list_all()
        idx = {}
        for plant_photo in plant_photo_list:
            key = get_key(plant_photo)
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
            confidence = plant_net_result.top_confidence
            if not confidence:
                continue
            if key not in idx:
                idx[key] = []
            idx[key].append(confidence)
        return idx

    @staticmethod
    def get_lines_for_key(label, get_key):
        COLORS_LIST = ['brown', 'red', 'orange', 'green']
        MIN_N = 15

        idx = ReadMeIdentification.get_analysis_by_key(get_key)

        if label in ['species', 'family']:

            def key(x):
                return sum(x[1]) / len(x[1])

        else:

            def key(x):
                return x[0]

        sorted_idx_items = sorted(idx.items(), key=key)

        x = []
        y = []
        x_mean = []
        y_mean = []
        y_mean_q1 = []
        y_mean_q3 = []
        color = []

        for key, conf_list in sorted_idx_items:
            sorted_conf_list = sorted(conf_list)
            n = len(sorted_conf_list)
            if n < MIN_N:
                continue

            x_mean.append(key)
            mean = sum(sorted_conf_list) / n

            y_mean.append(mean)
            y_mean_q1.append(sorted_conf_list[n // 4])
            y_mean_q3.append(sorted_conf_list[3 * n // 4])

            for i, conf in enumerate(sorted_conf_list):
                x.append(key)
                y.append(conf)
                color.append(COLORS_LIST[int(len(COLORS_LIST) * i / n)])

        plt.close()
        plt.figure(figsize=(16, 9))
        plt.tight_layout(pad=2.0)
        plt.xticks(rotation='vertical')

        plt.scatter(x, y, color=color, alpha=0.3, s=100, edgecolors='none')
        plt.plot(
            x_mean, y_mean, color='black', linewidth=2, linestyle='dashed'
        )
        plt.fill_between(
            x_mean, y_mean_q1, y_mean_q3, color='black', alpha=0.1
        )

        plt.xlabel(label.title())
        plt.ylabel('Confidence')
        plt.title(f'Plant Identification Confidence by {label.title()}')

        id = label.replace(' ', '-')
        chart_path = os.path.join('images', f'identification.{id}.png')
        plt.savefig(chart_path)
        plt.close()

        log.debug(f'Wrote {chart_path}')
        os.startfile(chart_path)

        chart_path_unix = chart_path.replace('\\', '/')

        lines = [
            '### ' + label.title(),
            '',
            Markdown.image(chart_path_unix, chart_path_unix),
            '',
        ]
        return lines

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
    def lines_lat(self):
        def get_key(plant_photo):
            Q = 0.0001

            return round(plant_photo.latlng.lat / Q) * Q

        return self.get_lines_for_key('lat', get_key)

    @cached_property
    def lines_lng(self):
        def get_key(plant_photo):
            Q = 0.0002
            return round(plant_photo.latlng.lng / Q) * Q

        return self.get_lines_for_key('lng', get_key)

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
            + self.lines_lat
            + self.lines_lng
            + ['']
        )
