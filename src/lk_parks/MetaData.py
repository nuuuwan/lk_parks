import os
from dataclasses import dataclass
from functools import cache

from exif import Image as ExifImage
from PIL import Image as PILImage
from utils import TIME_FORMAT_TIME, File, JSONFile, Log, Time, TimeFormat

log = Log('MetaData')


@dataclass
class MetaData:
    original_image_path: str
    image_path: str
    ut: int
    latlng: tuple[float, float]
    alt: float
    direction: float

    TIME_FORMAT_EXIF = TimeFormat('%Y:%m:%d %H:%M:%S')
    VALID_IMAGE_EXT_LIST = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']

    DIR_IMAGES = os.path.join('data', 'images')
    DIR_IMAGES_ORIGINAL = os.path.join('data', 'images_original')
    JSON_DATA_PATH = os.path.join('data', 'metadata.json')
    README_PATH = os.path.join('README.md')

    IMAGE_WIDTH = 960

    def __dict__(self) -> dict:
        return dict(
            image_path=self.image_path,
            ut=self.ut,
            latlng=self.latlng,
            alt=self.alt,
            direction=self.direction,
        )

    @staticmethod
    def from_hms(hms):
        h, m, s = hms
        return round(h + m / 60 + s / 3600, 6)

    @staticmethod
    def resize_image(original_image_path: str) -> str:
        image_name = os.path.basename(original_image_path)
        image_name = image_name.replace(' ', '-').replace(',', '')
        image_path = os.path.join(MetaData.DIR_IMAGES, image_name)
        if not os.path.exists(image_path):
            im = PILImage.open(original_image_path)
            w, h = im.size
            new_w = MetaData.IMAGE_WIDTH
            new_h = int(h * new_w / w)
            im = im.resize((new_w, new_h))
            im.save(image_path)
            log.debug(
                f'Resized {original_image_path} ({w}x{h})'
                + f' to {image_path} ({new_w}x{new_h})'
            )
        return image_path

    @staticmethod
    @cache
    def from_original_image(original_image_path: str) -> 'MetaData':
        with open(original_image_path, 'rb') as src:
            img = ExifImage(src)
            ut = int(
                MetaData.TIME_FORMAT_EXIF.parse(img.datetime_original).ut
            )
            latlng = (
                MetaData.from_hms(img.gps_latitude),
                MetaData.from_hms(img.gps_longitude),
            )
            alt = img.gps_altitude
            direction = img.gps_img_direction

            image_path = MetaData.resize_image(original_image_path)

            return MetaData(
                original_image_path, image_path, ut, latlng, alt, direction
            )

    @property
    def time_str(self) -> str:
        return TIME_FORMAT_TIME.stringify(Time(self.ut))

    @property
    def google_maps_link(self) -> str:
        lat, lng = self.latlng
        url = f'https://www.google.com/maps/place/{lat}N,{lng}E'
        label = f'{lat:.4f}°N,{lng:.4f}°E'
        return f'[{label}]({url})'

    @property
    def image_path_unix(self) -> str:
        return self.image_path.replace('\\', '/')

    @property
    def direction_humanized(self) -> str:
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
        return directions[round(self.direction / 45) % 8]

    @property
    def description_lines(self):
        return [
            '|  |  |',
            '| --- | --- |',
            f'| **Time** | {self.time_str} |',
            f'| **Location** | {self.google_maps_link} |',
            f'| **Altitude** | {self.alt:.1f}m |',
            f'| **Camera Direction** | {self.direction_humanized}'
            + f' ({self.direction:.0f}°) |',
        ]

    @property
    def title(self) -> str:
        return f'🌳 {self.google_maps_link} ({self.time_str})'

    # lists

    @staticmethod
    @cache
    def original_image_path_list() -> list[str]:
        original_image_path_list = []
        for file_name in os.listdir(MetaData.DIR_IMAGES_ORIGINAL):
            ext = file_name.split('.')[-1]
            if ext not in MetaData.VALID_IMAGE_EXT_LIST:
                continue
            original_image_path = os.path.join(
                MetaData.DIR_IMAGES_ORIGINAL, file_name
            )
            original_image_path_list.append(original_image_path)
        return original_image_path_list

    @staticmethod
    @cache
    def list_all():
        unsorted_list = [
            MetaData.from_original_image(img_path)
            for img_path in MetaData.original_image_path_list()
        ]
        sorted_list = sorted(unsorted_list, key=lambda md: md.latlng[0] * 3_600 + md.latlng[1])
        return sorted_list

    @staticmethod
    def save_all():
        d_list = []
        for md in MetaData.list_all():
            d = md.__dict__()
            d_list.append(d)
        JSONFile(MetaData.JSON_DATA_PATH).write(d_list)
        n = len(d_list)
        log.info(f'Saved {n} images to {MetaData.JSON_DATA_PATH}')

    @staticmethod
    def build_readme():
        lines = ['# Viharamahadevi Park, Colombo, Sri Lanka', '']
        for md in MetaData.list_all():
            lines.append(f'## {md.title}')
            lines.append('')
            lines.extend(md.description_lines)
            lines.append('')
            lines.append(f'![{md.image_path_unix}]({md.image_path_unix})')
            lines.append('')
        File(MetaData.README_PATH).write_lines(lines)
        log.debug(f'Wrote {MetaData.README_PATH}')
