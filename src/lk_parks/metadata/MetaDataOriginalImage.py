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
    DIR_DATA_IMAGES_ORIGINAL = os.path.join('data', 'images_original')

    IMAGE_WIDTH = 960

    @staticmethod
    def from_hms(hms):
        h, m, s = hms
        return round(h + m / 60 + s / 3600, 6)

    @staticmethod
    def get_image_path(original_image_path: str) -> str:
        image_name = os.path.basename(original_image_path)
        image_name = image_name.replace(' ', '-').replace(',', '')
        image_path = os.path.join(
            MetaDataOriginalImage.DIR_DATA_IMAGES, image_name)
        return image_path

    @staticmethod
    def resize_image(original_image_path: str, image_path: str) -> str:
        if not os.path.exists(image_path):
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
        return image_path

    @classmethod
    def from_original_image(cls, original_image_path: str):
        with open(original_image_path, 'rb') as src:
            image_path = MetaDataOriginalImage.get_image_path(
                original_image_path)
            if os.path.exists(image_path):
                return None
            MetaDataOriginalImage.resize_image(original_image_path, image_path)

            img = ExifImage(src)
            ut = int(
                MetaDataOriginalImage.TIME_FORMAT_EXIF.parse(
                    img.datetime_original).ut
            )
            latlng = (
                MetaDataOriginalImage.from_hms(img.gps_latitude),
                MetaDataOriginalImage.from_hms(img.gps_longitude),
            )
            alt = img.gps_altitude
            try:
                direction = img.gps_img_direction
            except AttributeError:
                direction = None

            plantnet_results = PlantNet.from_env().identify(image_path)

            return cls(
                original_image_path,
                image_path,
                ut,
                latlng,
                alt,
                direction,
                plantnet_results,
            )

    @staticmethod
    def original_image_path_list() -> list[str]:
        original_image_path_list = []
        for file_name in os.listdir(
                MetaDataOriginalImage.DIR_DATA_IMAGES_ORIGINAL):
            ext = file_name.split('.')[-1]
            if ext not in MetaDataOriginalImage.VALID_IMAGE_EXT_LIST:
                continue
            if '(' in file_name:
                continue 
            original_image_path = os.path.join(
                MetaDataOriginalImage.DIR_DATA_IMAGES_ORIGINAL, file_name
            )
            original_image_path_list.append(original_image_path)
        return original_image_path_list

    @classmethod
    def build_from_dir_data_image_original(cls):
        for img_path in MetaDataOriginalImage.original_image_path_list():
            md = cls.from_original_image(img_path)
            if md is not None:
                md.write()
