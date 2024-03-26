from functools import cached_property
import random
from lk_plants.analysis.InfoReadMe import InfoReadMe
from utils_future import MarkdownPage
from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto
from lk_plants.core.plant_net.PlantNetResult import PlantNetResult


class ReadMeDifficultIds(MarkdownPage, InfoReadMe):
    MIN_CONFIDENCE = 0.1
    
    @cached_property
    def file_path(self):
        return 'README.difficult_ids.md'

    @staticmethod
    def is_difficult(plant_photo: PlantPhoto) -> bool:
        plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
        species_name_to_score = plant_net_result.species_name_to_score
        if not species_name_to_score:
            return False
        score = list(species_name_to_score.values())[0]
        return score < ReadMeDifficultIds.MIN_CONFIDENCE
            

    @cached_property
    def lines_inner(self) -> list[str]:
        plant_photos = PlantPhoto.list_all()
        plant_photos_difficult = [
            plant_photo for plant_photo in plant_photos
            if ReadMeDifficultIds.is_difficult(plant_photo)
        ]
        random.shuffle(plant_photos_difficult)
        MAX_DISPLAY_PHOTOS = 20
        MAX_DISPLAY_SCORES = 3

        plant_photos_difficult = plant_photos_difficult[:MAX_DISPLAY_PHOTOS]
        image_lines = []
        for plant_photo in plant_photos_difficult:
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
            species_name_to_score = plant_net_result.species_name_to_score
            score_lines = []
            for species_name, score in list(species_name_to_score.items())[:MAX_DISPLAY_SCORES]:
                score_lines.append(f'* {score:.1%} *{species_name}*')

            image_path = plant_photo.image_path
            image_path_unix = image_path.replace('\\', '/')

            image_lines.extend([
                '### ' + plant_photo.id,
                '',
                '\n'.join(score_lines),
                '',
                f'![{plant_photo.id}]({image_path_unix})',
                '',
            ])
        return image_lines

    @cached_property
    def lines(self) -> list[str]:
        return [
            '## Plant Photos difficult to Identify',
            '',
            'Examples of Plant Photos where the identification confidence '+f'is < {ReadMeDifficultIds.MIN_CONFIDENCE:.0%}.',
            '',
            
        ] + self.lines_inner
