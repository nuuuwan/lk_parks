import os
from dataclasses import dataclass

from exif import Image as ExifImage
from PIL import Image as PILImage
from utils import Log, TimeFormat

from plantnet import PlantNet

log = Log('MetaData')


@dataclass
class MetaDataOriginalImage:

    TIME_FORMAT_EXIF = TimeFormat('%Y:%m:%d %H:%M:%S')
    VALID_IMAGE_EXT_LIST = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']

    DIR_DATA_IMAGES = os.path.join('data', 'images')
    DIR_DATA_original_images = os.path.join('data', 'original_images')

    IMAGE_WIDTH = 960

    @staticmethod
    def from_hms(hms):
        h, m, s = hms
        return round(h + m / 60 + s / 3600, 6)

    @staticmethod
    def parse_latlng(img):
        lat = MetaDataOriginalImage.from_hms(img.gps_latitude)
        lng = MetaDataOriginalImage.from_hms(img.gps_longitude)
        return lat, lng

    @staticmethod
    def get_image_path(original_image_path: str) -> str:
        image_name = os.path.basename(original_image_path)
        image_name = image_name.replace(' ', '-').replace(',', '')
        image_path = os.path.join(
            MetaDataOriginalImage.DIR_DATA_IMAGES, image_name)
        return image_path

    @staticmethod
    def resize_image(original_image_path: str) -> str:
        image_path = MetaDataOriginalImage.get_image_path(
            original_image_path)
        if os.path.exists(image_path):
            return

        im = PILImage.open(original_image_path)
        w, h = im.size
        new_w = MetaDataOriginalImage.IMAGE_WIDTH
        new_h = int(h * new_w / w)
        im = im.resize((new_w, new_h))
        im.save(image_path)
        log.debug(
            f'Resized {original_image_path} ({w}x{h})'
            + f' to {image_path} ({new_w}x{new_h})'
        )

    @staticmethod
    def parse_direction(img, original_image_path):
        try:
            return img.gps_img_direction
        except Exception as e:
            log.error(f'No direction in {original_image_path}: ' + str(e))
            return None

    @staticmethod
    def parse_ut(img):
        return int(
            MetaDataOriginalImage.TIME_FORMAT_EXIF.parse(
                img.datetime_original).ut
        )

    @classmethod
    def from_original_image(cls, original_image_path: str):
        MetaDataOriginalImage.resize_image(original_image_path)
        image_path = MetaDataOriginalImage.get_image_path(original_image_path)
        assert os.path.exists(image_path)

        metadata_path = cls.get_metadata_path(image_path)
        assert not os.path.exists(metadata_path)

        with open(original_image_path, 'rb') as src:
            img = ExifImage(src)
            ut = MetaDataOriginalImage.parse_ut(img)
            latlng = MetaDataOriginalImage.parse_latlng(img)
            alt = img.gps_altitude
            direction = MetaDataOriginalImage.parse_direction(
                img, original_image_path)
            plantnet_results = PlantNet.from_env().identify(image_path)
            md = cls(
                original_image_path,
                image_path,
                ut,
                latlng,
                alt,
                direction,
                plantnet_results,
            )

            md.write()

            return md

    @staticmethod
    def original_image_path_list() -> list[str]:
        original_image_path_list = []
        for file_name in os.listdir(
                MetaDataOriginalImage.DIR_DATA_original_images):
            ext = file_name.split('.')[-1]
            if ext not in MetaDataOriginalImage.VALID_IMAGE_EXT_LIST:
                continue
            if '(' in file_name:
                continue
            original_image_path = os.path.join(
                MetaDataOriginalImage.DIR_DATA_original_images, file_name
            )
            original_image_path_list.append(original_image_path)
        return original_image_path_list

    @classmethod
    def build_from_dir_data_original_image(cls):
        n = 0
        n_new = 0
        n_has_metadata = 0
        n_error = 0

        for original_image_path in MetaDataOriginalImage.original_image_path_list():
            n += 1

            image_path = MetaDataOriginalImage.get_image_path(
                original_image_path)

            metadata_path = cls.get_metadata_path(image_path)
            if os.path.exists(metadata_path):
                n_has_metadata += 1
                continue

            cls.from_original_image(original_image_path)
            n_new += 1

        log.debug(f'{n_has_metadata=}')
        log.warn(f'{n_error=}')
        log.info(f'Processed {n_new}/{n} images.')
