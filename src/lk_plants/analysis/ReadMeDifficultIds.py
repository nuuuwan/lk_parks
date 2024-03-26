from functools import cached_property
import random
from lk_plants.analysis.InfoReadMe import InfoReadMe
from utils_future import MarkdownPage
from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto
from lk_plants.core.plant_net.PlantNetResult import PlantNetResult


class ReadMeDifficultIds(MarkdownPage, InfoReadMe):
    @cached_property
    def file_path(self):
        return 'README.difficult_ids.md'

    @cached_property
    def lines_inner(self) -> list[str]:
        plant_photos = PlantPhoto.list_all()
        plant_photos_difficult = [
            plant_photo for plant_photo in plant_photos
            if list(PlantNetResult.from_plant_photo(plant_photo).species_name_to_score.values())[0] < PlantNetResult.MIN_CONFIDENCE
        ]
        random.shuffle(plant_photos_difficult)
        N_DISPLAY = 20
        N_COLUMNS = 3
        plant_photos_difficult = plant_photos_difficult[:N_DISPLAY]
        image_lines = []
        for i, plant_photo in enumerate(plant_photos_difficult):
            if i % N_COLUMNS == 0:
                image_lines.append('')
            image_lines.append(
                f'![{plant_photo.image_name}]({plant_photo.image_path})'
            )
        return image_lines

    @cached_property
    def lines(self) -> list[str]:
        return [
            '## Plant Photos difficult to Identify',
            '',
            self.lines_inner
        ]
