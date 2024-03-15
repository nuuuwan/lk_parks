import os

import cv2
import numpy as np
from PIL import Image, ImageEnhance
from utils import Log

from lk_parks import PlantNetResult

log = Log('test_plant_net')


def increase_saturation(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    image[:, :, 1] = image[:, :, 1] * 2
    image[:, :, 1] = np.clip(image[:, :, 1], 0, 255)

    image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
    image_path = image_path.replace('.jpg', '.saturated.jpg')
    cv2.imwrite(image_path, image)
    log.info(f'Wrote {image_path}')


def enhance(image_path, factor):
    im = Image.open(image_path)
    enhancer = ImageEnhance.Contrast(im)
    im2 = enhancer.enhance(factor)
    image_path = image_path.replace('.jpg', f'.enhanced.{factor}.jpg')
    im2.save(image_path)
    log.info(f'Wrote {image_path}')


def edge_detect(image_path):
    # Load the image from the file
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Apply Canny edge detection
    edges = cv2.Canny(image, 100, 200)

    # Save the result to a file

    image_path = image_path.replace('.jpg', '.edges.jpg')
    cv2.imwrite(image_path, edges)
    log.info(f'Wrote {image_path}')


def increase_contrast(image_path):
    # Load the image from the file
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    # Convert the image to YUV color space
    img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)

    # Apply histogram equalization on the Y channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img_yuv[:, :, 0] = clahe.apply(img_yuv[:, :, 0])

    # Convert the image back to RGB color space
    image = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

    # Save the result to a file

    image_path = image_path.replace('.jpg', '.contrast.jpg')
    cv2.imwrite(image_path, image)
    log.info(f'Wrote {image_path}')


def sharpen(image_path):
    image = cv2.imread(image_path)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])

    sharpened = cv2.filter2D(image, -1, kernel)

    image_path = image_path.replace('.jpg', '.sharpened.jpg')
    cv2.imwrite(image_path, sharpened)
    log.info(f'Wrote {image_path}')


def build_test_images():
    for image_id in ['resized']:
        image_path = os.path.join('data_test', f'{image_id}.jpg')
        log.debug(f'Building from {image_path}...')
        # enhance(image_path, 2)
        increase_saturation(image_path)


def main():
    for file_name in os.listdir('data_test'):
        if not file_name.endswith('.jpg'):
            continue
        image_path = os.path.join('data_test', file_name)
        log.info('-' * 32)
        log.info(f'Testing {image_path}...')
        results = PlantNetResult.identify(image_path)
        for result in results[:5]:
            species = result['species']['scientificNameWithoutAuthor']
            score = result['score']
            log.info(f'{species} ({score:.0%})')


if __name__ == "__main__":
    build_test_images()
    main()
