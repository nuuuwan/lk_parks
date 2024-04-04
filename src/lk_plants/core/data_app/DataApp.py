import os

from utils import JSONFile, Log

from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto
from lk_plants.core.taxonomy.Species import Species
from lk_plants.core.wiki.WikiPage import WikiPage

log = Log('DataApp')


class DataApp:
    DIR_DATA_APP = 'data_app'

    @staticmethod
    def get_summary_short(summary):
        MAX_LEN_SUMMARY = 500
        paragraphs = summary.split('\n\n')
        content = ''
        for word in paragraphs[0].split(' '):
            if len(content) + len(word) + 1 > MAX_LEN_SUMMARY:
                content += '...'
                break
            content += word + ' '
        return content.strip()

    @staticmethod
    def get_data_long(plant_photo):
        d = plant_photo.to_dict()
        plant_new_result = PlantNetResult.from_plant_photo(plant_photo)
        d['plant_net_result'] = plant_new_result.to_dict()

        species_names = list(plant_new_result.species_name_to_score.keys())
        if species_names:
            species_name = species_names[0]
            species = Species.from_name(species_name)
            d['species'] = species.to_dict()

            d['wiki_page'] = WikiPage.from_wiki_page_name(
                species.wiki_page_name
            ).to_dict()
        return d

    @staticmethod
    def get_data_short(plant_photo):
        d = DataApp.get_data_long(plant_photo)
        if not d:
            return None

        # cleanup
        del d['original_image_path']
        del d['alt']

        MAX_SPECIES = 5
        d['plant_net_result']['species_name_to_score'] = dict(
            list(d['plant_net_result']['species_name_to_score'].items())[
                :MAX_SPECIES
            ]
        )
        del d['plant_net_result']['ut_api_call']
        del d['plant_net_result']['plant_photo_id']

        if 'species' in d:
            del d['species']['gbif_id']
            del d['species']['powo_id']
            del d['species']['iucn_id']
            # del d['species']['iucn_category']

        if 'wiki_page' in d:
            del d['wiki_page']['wiki_page_name']
            d['wiki_page']['summary_short'] = DataApp.get_summary_short(
                d['wiki_page']['summary']
            )
            del d['wiki_page']['summary']
        return d

    @staticmethod
    def get_ext_plant_photo_idx(func_get_data):
        plant_photo_list = PlantPhoto.list_all()
        idx = {}
        for plant_photo in plant_photo_list:
            d = func_get_data(plant_photo)
            if not d:
                continue
            idx[plant_photo.id] = d
        return idx

    @staticmethod
    def write_ext_plant_photo_idx(func_get_data, label):
        idx = DataApp.get_ext_plant_photo_idx(func_get_data)

        data_idx_path = os.path.join(
            DataApp.DIR_DATA_APP, f'ext_plant_photo_idx{label}.json'
        )
        JSONFile(data_idx_path).write(idx)
        file_size_m = os.path.getsize(data_idx_path) / 1_000_000
        log.info(f'Wrote {len(idx)} extended plant photos to ')
        log.info(f'{data_idx_path} ({file_size_m:.01f}MB)')

    @staticmethod
    def write_all():
        DataApp.write_ext_plant_photo_idx(DataApp.get_data_short, '')
        DataApp.write_ext_plant_photo_idx(DataApp.get_data_long, '.long')
