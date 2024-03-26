import os
import time
from dataclasses import dataclass
from functools import cache

import wikipediaapi
from utils import JSONFile, Log

from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto
from lk_plants.core.taxonomy import Species

log = Log('WikiPage')


@dataclass
class WikiPage:
    wiki_page_name: str
    summary: str

    PROJECT = 'nuuuwan.lk_plants'
    LANG = 'en'
    DIR_DATA_WIKI = os.path.join(
        'data',
        'wiki',
    )

    def to_dict(self) -> dict:
        return self.__dict__

    @classmethod
    def get_data_path(cls, wiki_page_name: str) -> str:
        if not os.path.exists(WikiPage.DIR_DATA_WIKI):
            os.makedirs(WikiPage.DIR_DATA_WIKI)
        return os.path.join(
            WikiPage.DIR_DATA_WIKI,
            f'{wiki_page_name.lower()}.json',
        )

    @property
    def data_path(self) -> str:
        return WikiPage.get_data_path(self.wiki_page_name)

    def write(self):
        JSONFile(self.data_path).write(self.to_dict())
        log.info(f'Wrote {self.data_path}')

    @staticmethod
    @cache
    def get_wiki_page_name_from_plant_photo(plant_photo: PlantPhoto) -> str:
        plant_net_result = PlantNetResult.from_plant_photo(plant_photo)
        top_species_name = plant_net_result.top_species_name
        species = Species.from_name(top_species_name)
        wiki_page_name = species.wiki_page_name
        return wiki_page_name

    @staticmethod
    def filter_with_no_results(plant_photo: PlantPhoto):
        wiki_page_name = WikiPage.get_wiki_page_name_from_plant_photo(
            plant_photo
        )
        data_path = WikiPage.get_data_path(wiki_page_name)
        return not os.path.exists(data_path)

    @staticmethod
    def call_wiki_api(wiki_page_name: str):
        time.sleep(1)
        wiki = wikipediaapi.Wikipedia(WikiPage.PROJECT, WikiPage.LANG)
        page = wiki.page(wiki_page_name)
        return page

    @staticmethod
    def from_plant_photo(plant_photo: PlantPhoto) -> 'WikiPage':
        wiki_page_name = WikiPage.get_wiki_page_name_from_plant_photo(
            plant_photo
        )
        page = WikiPage.call_wiki_api(wiki_page_name)
        wiki_page = WikiPage(
            wiki_page_name=wiki_page_name, summary=page.summary
        )
        wiki_page.write()
        return wiki_page

    @staticmethod
    def build_from_plant_photos():
        plant_photo_list = PlantPhoto.list_all()
        plant_photo_list_filtered = [
            plant_photo
            for plant_photo in plant_photo_list
            if WikiPage.filter_with_no_results(plant_photo)
        ]
        n_filtered = len(plant_photo_list_filtered)
        log.debug(f'{n_filtered=}')

        for i, plant_photo in enumerate(plant_photo_list_filtered):
            log.debug(f'{i + 1}/{n_filtered}')
            WikiPage.from_plant_photo(plant_photo)
        log.info('build_from_plant_photos: done')
