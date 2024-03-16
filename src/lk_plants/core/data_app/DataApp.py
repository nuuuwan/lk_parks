import os

from utils import JSONFile, Log

from lk_plants.core.plant_net.PlantNetResult import PlantNetResult
from lk_plants.core.plant_photo.PlantPhoto import PlantPhoto
from lk_plants.core.taxonomy.Species import Species

log = Log('DataApp')


class DataApp:
    DIR_DATA_APP = 'data_app'
    EXT_PLANT_PHOTO_IDX_PATH = os.path.join(
        DIR_DATA_APP, 'ext_plant_photo_idx.json')

    def ext_plant_photo_idx(self):
        plant_photo_list = PlantPhoto.list_all()
        idx = {}
        for plant_photo in plant_photo_list:
            d = plant_photo.to_dict()
            plant_new_result = PlantNetResult.from_plant_photo(plant_photo)
            d['plant_net_result'] = plant_new_result.to_dict()

            species_names = list(plant_new_result.species_name_to_score.keys())
            if not species_names:
                continue
            species_name = species_names[0]
            species = Species.from_name(species_name)
            d['species'] = species.to_dict()

            idx[plant_photo.id] = d

        return idx

    def write_ext_plant_photo_idx(self):
        idx = self.ext_plant_photo_idx()
        JSONFile(DataApp.EXT_PLANT_PHOTO_IDX_PATH).write(idx)
        file_size_k = os.path.getsize(DataApp.EXT_PLANT_PHOTO_IDX_PATH) / 1_000
        log.info(
            f'Wrote {len(idx)} extended plant photos to ' +
            f'{DataApp.EXT_PLANT_PHOTO_IDX_PATH} ({file_size_k:.01f}KB)')

    def write_all(self):
        self.write_ext_plant_photo_idx()
