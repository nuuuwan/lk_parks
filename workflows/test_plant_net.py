from lk_parks import PlantNetResult
from utils import Log
import os
log = Log('test_plant_net')

def main():
    for image_id in ['Photo-2023-12-31-07-53-22']:
        image_path = os.path.join('data', 'images', f'{image_id}.jpg')
        log.info('-' * 32)
        log.info(f'Testing {image_path}...')
        results = PlantNetResult.identify(image_path)
        for result in results[:5]:
            species = result['species']['scientificNameWithoutAuthor']
            score = result['score']
            log.info(f'{species} ({score:.0%})')

if __name__ == "__main__":
    main()