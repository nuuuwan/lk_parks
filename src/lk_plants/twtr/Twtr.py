import random
from functools import cached_property

from twtr import Tweet, Twitter
from utils import Log

from lk_plants.analysis import InfoReadMe
from lk_plants.core import PlantNetResult, PlantPhoto, Species, WikiPage
from lk_plants.twtr.AnnotatedImage import AnnotatedImage

log = Log('Twtr')


class Twtr(AnnotatedImage):
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

    def tweet(self):
        text = self.tweet_text
        log.debug(text)
        image_path = self.annotated_image_path
        log.debug(f'{image_path=}')

        twitter = Twitter()
        tweet = Tweet(text).add_image(image_path)
        tweet_id = twitter.send(tweet)
        log.debug(f'{tweet_id=}')
        if not tweet_id:
            raise Exception('Null tweet_id')
