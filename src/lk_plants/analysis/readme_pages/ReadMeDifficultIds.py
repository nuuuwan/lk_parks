from functools import cached_property

from lk_plants.analysis.InfoReadMe import InfoReadMe
from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto
from utils_future import Markdown, MarkdownPage


class ReadMeDifficultIds(MarkdownPage, InfoReadMe):
    MIN_CONFIDENCE = 0.2

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
            plant_photo
            for plant_photo in plant_photos
            if ReadMeDifficultIds.is_difficult(plant_photo)
        ]
        MAX_DISPLAY_PHOTOS = 20
        MAX_DISPLAY_SCORES = 3

        plant_photos_difficult = plant_photos_difficult[-MAX_DISPLAY_PHOTOS:]
        image_lines = []
        for plant_photo in plant_photos_difficult:
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
            species_name_to_score = plant_net_result.species_name_to_score
            score_lines = []
            for species_name, score in list(species_name_to_score.items())[
                :MAX_DISPLAY_SCORES
            ]:
                score_lines.append(f'* {score:.1%} *{species_name}*')

            image_path = plant_photo.image_path
            image_path_unix = image_path.replace('\\', '/')

            image_lines.extend(
                [
                    '### ' + plant_photo.id,
                    '',
                    '\n'.join(score_lines),
                    '',
                    Markdown.image_html(
                        plant_photo.id, image_path_unix, width='50%'
                    ),
                    '',
                ]
            )
        return image_lines

    @cached_property
    def lines(self) -> list[str]:
        return [
            '## Sample of Recent Plant Photos difficult to Identify',
            '',
            'Photos where the identification confidence '
            + f'is **< {ReadMeDifficultIds.MIN_CONFIDENCE:.0%}**.',
            '',
        ] + self.lines_inner
