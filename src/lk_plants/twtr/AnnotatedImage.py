import os
import tempfile
from functools import cached_property

from PIL import Image, ImageDraw, ImageFont
from utils import Log

log = Log('AnnotatedImage')


class AnnotatedImage:
    @staticmethod
    def draw_box(img, text_width, text_height, PADDING):
        width, height = img.size
        img_overlay = Image.new('RGBA', img.size)
        draw = ImageDraw.Draw(img_overlay)
        rectangle_color = (0, 0, 0, 128)  # semi-transparent black
        draw.rectangle(
            [
                (
                    width - text_width - PADDING * 3,
                    height - text_height - PADDING * 3,
                ),
                (width - PADDING, height - PADDING),
            ],
            fill=rectangle_color,
        )
        img = Image.alpha_composite(img, img_overlay)
        return img

    @staticmethod
    def draw_text(img, text):
        width, height = img.size

        draw = ImageDraw.Draw(img)
        font_path = os.path.join('fonts', 'p22.ttf')
        font = ImageFont.truetype(font_path, 48)

        PADDING = 10
        text_width, text_height = draw.textsize(text, font)

        img = AnnotatedImage.draw_box(img, text_width, text_height, PADDING)

        draw = ImageDraw.Draw(img)
        text_color = (255, 255, 255, 255)
        draw.text(
            (
                width - text_width - PADDING * 2,
                height - text_height - PADDING * 2,
            ),
            text,
            font=font,
            fill=text_color,
        )
        return img

    @cached_property
    def annotated_image_path(self) -> str:
        image_path = image_path = self.plant_photo.image_path
        if os.name != 'nt':
            image_path = image_path.replace('\\', '/')
        with Image.open(image_path) as img:
            img = img.convert('RGBA')

            text = self.species.name
            img = AnnotatedImage.draw_text(img, text)
            tmp_image_path = tempfile.mktemp(suffix='.png')
            img.save(tmp_image_path)
            log.debug(f'{tmp_image_path=}')
            if os.name == 'nt':
                os.startfile(tmp_image_path)
            return tmp_image_path
