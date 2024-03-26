import os
import time
from dataclasses import dataclass
from functools import cache

import wikipediaapi
from utils import JSONFile, Log

from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto
from lk_plants.core.taxonomy.Species import Species

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
    T_SLEEP_CALL_API = 1

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
        if not top_species_name:
            return None
        species = Species.from_name(top_species_name)
        wiki_page_name = species.wiki_page_name
        return wiki_page_name

    @staticmethod
    @cache
    def get_wiki_page_name_list() -> list[str]:
        plant_photo_list = PlantPhoto.list_all()
        wiki_page_name_list = [
            WikiPage.get_wiki_page_name_from_plant_photo(plant_photo)
            for plant_photo in plant_photo_list
        ]
        wiki_page_name_list_filtered = [
            wiki_page_name
            for wiki_page_name in wiki_page_name_list
            if wiki_page_name
            and not os.path.exists(WikiPage.get_data_path(wiki_page_name))
        ]
        wiki_page_name_list_unique = sorted(
            list(set(wiki_page_name_list_filtered))
        )
        return wiki_page_name_list_unique

    @staticmethod
    def call_wiki_api(wiki_page_name: str):
        time.sleep(WikiPage.T_SLEEP_CALL_API)
        wiki = wikipediaapi.Wikipedia(WikiPage.PROJECT, WikiPage.LANG)
        page = wiki.page(wiki_page_name)
        return page

    @staticmethod
    def from_wiki_page_name(wiki_page_name: str) -> 'WikiPage':
        if os.path.exists(WikiPage.get_data_path(wiki_page_name)):
            wiki_page = JSONFile(
                WikiPage.get_data_path(wiki_page_name)
            ).read()
            return WikiPage(**wiki_page)

        page = WikiPage.call_wiki_api(wiki_page_name)
        summary = page.summary
        wiki_page = WikiPage(wiki_page_name=wiki_page_name, summary=summary)
        log.debug(f'📃 {wiki_page_name}: {summary}')
        wiki_page.write()
        return wiki_page

    @staticmethod
    def build():
        wiki_page_name_list = WikiPage.get_wiki_page_name_list()
        n_pages = len(wiki_page_name_list)
        log.debug(f'{n_pages=}')

        for i, wiki_page_name in enumerate(wiki_page_name_list):
            log.debug(f'{i + 1}/{n_pages}')
            WikiPage.from_wiki_page_name(wiki_page_name)
        log.info('build_from_plant_photos: done')
