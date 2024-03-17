import os

import cv2
import numpy as np
from PIL import Image, ImageEnhance
from utils import Log

from lk_plants import PlantNetResult

log = Log('test_plant_net')


DIR_TEST = os.path.join('data_test','plantnet')

def main():
    for file_name in os.listdir(DIR_TEST):
        if not file_name.endswith('.jpg'):
            continue
        image_path = os.path.join(DIR_TEST, file_name)
        log.info('-' * 32)
        log.info(f'Testing {image_path}...')
        results = PlantNetResult.identify(image_path)
        for result in results[:5]:
            species = result['species']['scientificNameWithoutAuthor']
            score = result['score']
            log.info(f'{species} ({score:.0%})')


if __name__ == "__main__":
   
    main()
