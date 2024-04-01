import random
from functools import cached_property

from twtr import Tweet, Twitter
from utils import Log, Time, TimeFormat

from lk_plants.core import PlantNetResult, PlantPhoto, Species

log = Log('Twtr')


class Twtr:
    def __init__(self, plant_photo):
        self.plant_photo = plant_photo

    @staticmethod
    def random():
        plant_photos = PlantPhoto.list_all()
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
    def tweet_text(self):
        full_name = self.species.full_name
        n_full_name = len(full_name)

        n_common_names_max = 279 - 111 - n_full_name
        common_names_str = self.species.get_common_names_str(
            max_len=n_common_names_max
        )

        tweet_text = '\n'.join(
            [
                full_name,
                '',
                common_names_str,
                '',
                TimeFormat('%H:%M%p (%b %d, %Y)').stringify(
                    Time(self.plant_photo.ut)
                ),
                '#ViharamahadeviPark #Colombo',
                '#SriLanka 🇱🇰 @PlantNet',
                'https://nuuuwan.github.io/plants',
            ]
        )

        n_tweet_text = len(tweet_text)
        assert n_tweet_text <= 280, f'{n_tweet_text=}'
        return tweet_text

    @cached_property
    def tweet_image_path(self):
        return self.plant_photo.image_path

    def tweet(self):
        text = self.tweet_text
        log.debug(text)
        image_path = self.tweet_image_path
        log.debug(f'{image_path=}')
        
        twitter = Twitter()
        tweet = Tweet(text).add_image(image_path)
        tweet_id = twitter.send(tweet)
        log.debug(f'{tweet_id=}')
