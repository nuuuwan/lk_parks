from functools import cache, cached_property

from utils import File, Log, Time, TimeFormat

from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto
from lk_plants.core.taxonomy.Species import Species

log = Log('ViharamahadeviParkReport')


class ViharamahadeviParkReport:
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
        ]

    @cached_property
    def lines_background(self):
        return [
            '## Background',
            '',
            'Viharamahadevi Park (Sinhala: විහාරමහාදේවී උද්‍යානය; formerly Victoria Park, Sinhala: වික්ටෝරියා පාක්) is a public park located in Cinnamon Gardens, in [Colombo](https://en.wikipedia.org/wiki/Colombo), situated in front of the colonial-era Town Hall in Sri Lanka. It was built by the British colonial administration and is the oldest and largest park of Colombo. The park was originally named "Victoria Park" after Queen Victoria but was renamed after Queen Viharamahadevi, the mother of King Dutugamunu on July 18, 1958. [[Wikipedia](https://en.wikipedia.org/wiki/Viharamahadevi_Park)]',
            '',
            'Viharamahadevi Park is 24.27ha, and has an estimated [green cover](https://en.wikipedia.org/wiki/Vegetation) of 14.39ha (59% from the total area). The estimated crown cover 12.25ha (50%). [[Madurapperum et al](https://www.researchgate.net/publication/282250239_CrownTree_cover_of_Viharamahadevi_Park_Colombo)]',
            '',
            f'*This analysis was automatically generated on  **{self.time_str}**, '
            + f'and is based on  **{self.n_plant_photos}** plant photos.*',
            '',
            'Results can be directly inspected using [this app](https://nuuuwan.github.io/plants).',
            '',
            '![App](image.app.png)',
            '',
        ]

    @cached_property
    def lines_confusion(self):
        MIN_PHOTOS = 2
        lines = [
            f'## Pairs of Plant Species, likely confused during identification (at least {MIN_PHOTOS} times)',
            '',
        ]
        key_to_n = {}
        for data in self.data_list:
            plant_net_result = PlantNetResult.from_plant_photo(data)
            species_name_to_score = plant_net_result.species_name_to_score
            species_names = list(species_name_to_score.keys())
            if len(species_names) < 2:
                continue
            species_name_1, species_name_2 = species_names[:2]
            score_1 = species_name_to_score[species_name_1]
            score_2 = species_name_to_score[species_name_2]
            if score_1 > 2 * score_2:
                continue
            if species_name_1 > species_name_2:
                species_name_1, species_name_2 = (
                    species_name_2,
                    species_name_1,
                )
            key = f'{species_name_1} & {species_name_2}'
            if key not in key_to_n:
                key_to_n[key] = 0
            key_to_n[key] += 1

        lines_table = [
            f'| Species 1 | Species 2 | n(Photos) |',
            '|:---|:---|---:|',
        ]
        for key, n in sorted(key_to_n.items(), key=lambda x: -x[1]):
            if n < MIN_PHOTOS:
                continue
            species_name_1, species_name_2 = key.split(' & ')
            lines_table.append(
                f'| *{species_name_1}* | *{species_name_2}* | {n:,} |'
            )

        lines += lines_table
        lines.append('')
        return lines

    @cached_property
    def lines_identification_score(self):
        species_name_to_score_list = {}
        for data in self.data_list:
            plant_net_result = PlantNetResult.from_plant_photo(data)
            species_name_to_score = plant_net_result.species_name_to_score
            if not species_name_to_score:
                continue
            species_name = list(species_name_to_score.keys())[0]
            score = species_name_to_score[species_name]
            if species_name not in species_name_to_score_list:
                species_name_to_score_list[species_name] = []
            species_name_to_score_list[species_name].append(score)

        MIN_PHOTOS = 5
        lines = [
            f'## Identification Confidence (by Species with at least {MIN_PHOTOS} Photos)',
            '',
            '| Species | n(Photos) | Confidence (25th pctl.) | Confidence (Median) | Confidence (75th pctl.) |',
            '|:---|---:|---:|---:|---:|',
        ]
        sorted_items = sorted(
            species_name_to_score_list.items(),
            key=lambda x: sum(x[1]) / len(x[1]),
            reverse=True,
        )
        for species_name, scores in sorted_items:
            n = len(scores)
            if n < MIN_PHOTOS:
                continue

            i_low = int(n * 0.25)
            i_mid = int(n * 0.5)
            i_high = int(n * 0.75)
            sorted_scores = sorted(scores)
            low = sorted_scores[i_low]
            mid = sorted_scores[i_mid]
            high = sorted_scores[i_high]

            lines.append(
                f'| *{species_name}* | {n:,} | {low:.1%} | {mid:.1%} | {high:.1%} |'
            )
        lines.append('')
        return lines

    @cache
    def get_lines_analysis_by_key(self, label, get_key):
        key_to_data_list = {}
        for data in self.data_list:
            key = get_key(data)
            if key is None:
                continue
            if key not in key_to_data_list:
                key_to_data_list[key] = []
            key_to_data_list[key].append(data)

        n_unique = len(key_to_data_list)

        lines_table = [f'| {label} | n(Photos) | % |', '|:---|---:|---:|']
        N_DISPLAY = 20
        n_displayed = 0
        for key, data_list in sorted(
            key_to_data_list.items(), key=lambda x: -len(x[1])
        )[:N_DISPLAY]:
            n = len(data_list)
            p = n / self.n_plant_photos
            lines_table.append(f'| *{key}* | {n:,} | {p:.1%} |')
            n_displayed += n
        n_others = self.n_plant_photos - n_displayed
        p_others = n_others / self.n_plant_photos
        lines_table.append(
            f'| (All Others) | {n_others:,} | {p_others:.1%} |'
        )

        return (
            [
                f'### {label}',
                '',
                f'**{n_unique}** unique {label}.',
                '',
            ]
            + lines_table
            + ['']
        )

    @cached_property
    def lines_analysis_families(self):
        def get_key(plant_photo):
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
            species_name_to_score = plant_net_result.species_name_to_score
            if not species_name_to_score:
                return None
            species_name = list(species_name_to_score.keys())[0]
            species = Species.from_name(species_name)
            return species.genus.family.name

        return self.get_lines_analysis_by_key('Families', get_key)

    @cached_property
    def lines_analysis_genera(self):
        def get_key(plant_photo):
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
            species_name_to_score = plant_net_result.species_name_to_score
            if not species_name_to_score:
                return None
            species_name = list(species_name_to_score.keys())[0]
            species = Species.from_name(species_name)
            return species.genus.name

        return self.get_lines_analysis_by_key('Genera', get_key)

    @cached_property
    def lines_analysis_species(self):
        def get_key(plant_photo):
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
            species_name_to_score = plant_net_result.species_name_to_score
            if not species_name_to_score:
                return None
            species_name = list(species_name_to_score.keys())[0]
            return species_name

        return self.get_lines_analysis_by_key('Species', get_key)

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
