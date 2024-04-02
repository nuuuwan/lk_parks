import os
import random
import tempfile
from functools import cached_property

from PIL import Image, ImageDraw, ImageFont
from twtr import Tweet, Twitter
from utils import Log

from lk_plants.analysis import InfoReadMe
from lk_plants.core import PlantNetResult, PlantPhoto, Species, WikiPage

log = Log('Twtr')


class Twtr:
    MIN_SCORE = 0.2

    def __init__(self, plant_photo):
        self.plant_photo = plant_photo

    @staticmethod
    def is_suitable(plant_photo):
        if not InfoReadMe.is_in_geo(plant_photo):
            return False

        try:
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
        except BaseException:
            return False

        top_score = plant_net_result.top_confidence
        if not top_score:
            return False
        return top_score >= Twtr.MIN_SCORE

    @staticmethod
    def random():
        plant_photos = PlantPhoto.list_all()
        n_plant_photos = len(plant_photos)
        log.debug(f'{n_plant_photos=}')
        suitable_plant_photos = [
            plant_photo
            for plant_photo in plant_photos
            if Twtr.is_suitable(plant_photo)
        ]
        n_suitable_plant_photos = len(suitable_plant_photos)
        log.debug(f'{n_suitable_plant_photos=}')
        plant_photo = None
        while True:
            plant_photo = random.choice(plant_photos)
            plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
            if plant_net_result.top_species_name:
                break
        return Twtr(plant_photo)

    @cached_property
    def plant_net_result(self):
        return PlantNetResult.from_plant_photo(self.plant_photo)

    @cached_property
    def species(self):
        species_name = self.plant_net_result.top_species_name
        species = Species.from_name(species_name)
        return species

    @cached_property
    def wiki_page(self):
        return WikiPage.from_wiki_page_name(self.species.wiki_page_name)

    @cached_property
    def tweet_text_fixed(self):
        full_name = self.species.full_name
        tweet_text = '\n'.join(
            [
                full_name,
                '',
                '#ViharamahadeviPark, ' + '#SriLanka 🇱🇰',
                '',
                "https://en.wikipedia.org/wiki/"
                + self.wiki_page.wiki_page_name,
            ]
        )
        return tweet_text

    @cached_property
    def tweet_text(self):
        tweet_text_fixed = self.tweet_text_fixed
        n_tweet_text_fixed = len(tweet_text_fixed)

        n_common_names_str_max = 280 - n_tweet_text_fixed - 2
        common_names_str = self.species.get_common_names_str(
            max_len=n_common_names_str_max
        )

        tweet_text = '\n'.join(
            [
                common_names_str,
                '',
                tweet_text_fixed,
            ]
        )

        n_tweet_text = len(tweet_text)
        n_common_names_str = len(common_names_str)
        assert (
            n_tweet_text <= 280
        ), f'{n_tweet_text=} = {n_tweet_text_fixed=} + {n_common_names_str=}'
        return tweet_text

    def get_labelled_image_path(self):
        image_path = image_path = self.plant_photo.image_path
        if os.name != 'nt':
            image_path = image_path.replace('\\', '/')
        with Image.open(image_path) as img:
            img = img.convert('RGBA')

            width, height = img.size
            draw = ImageDraw.Draw(img)
            font_path = os.path.join('fonts', 'p22.ttf')
            font = ImageFont.truetype(font_path, 48)

            PADDING = 10
            text = self.species.name
            text_width, text_height = draw.textsize(text, font)

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

            tmp_image_path = tempfile.mktemp(suffix='.png')
            img.save(tmp_image_path)
            log.debug(f'{tmp_image_path=}')
            if os.name == 'nt':
                os.startfile(tmp_image_path)
            return tmp_image_path
        raise Exception('Failed to label image')

    def tweet(self):
        text = self.tweet_text
        log.debug(text)
        image_path = self.get_labelled_image_path()
        log.debug(f'{image_path=}')

        twitter = Twitter()
        tweet = Tweet(text).add_image(image_path)
        tweet_id = twitter.send(tweet)
        log.debug(f'{tweet_id=}')
        if not tweet_id:
            raise Exception('Null tweet_id')
