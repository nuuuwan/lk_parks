import os
import webbrowser
from dataclasses import dataclass
from functools import cache

from exif import Image
from utils import TIME_FORMAT_TIME, File, JSONFile, Log, Time, TimeFormat

log = Log('MetaData')


@dataclass
class MetaData:
    image_path: str
    ut: int
    latlng: tuple[float, float]
    alt: float
    direction: float

    TIME_FORMAT_EXIF = TimeFormat('%Y:%m:%d %H:%M:%S')

    DIR_IMAGES = os.path.join('data', 'images')
    JSON_DATA_PATH = os.path.join('data', 'metadata.json')
    README_PATH = os.path.join('README.md')

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
    @cache
    def from_image(img_path: str) -> 'MetaData':
        with open(img_path, 'rb') as src:
            img = Image(src)
            ut = int(
                MetaData.TIME_FORMAT_EXIF.parse(img.datetime_original).ut
            )
            latlng = (
                MetaData.from_hms(img.gps_latitude),
                MetaData.from_hms(img.gps_longitude),
            )
            alt = img.gps_altitude
            direction = img.gps_img_direction
            return MetaData(img_path, ut, latlng, alt, direction)

    def open_in_google_maps(self):
        lat, lng = self.latlng
        webbrowser.open(f'https://www.google.com/maps/place/{lat}N,{lng}E')

    @property
    def time_str(self) -> str:
        return TIME_FORMAT_TIME.stringify(Time(self.ut))

    @property
    def latlng_pretty(self) -> str:
        return f'{self.latlng[0]}°N,{self.latlng[1]}°E'

    @property
    def image_path_unix(self) -> str:
        return self.image_path.replace('\\', '/')

    @property
    def description_lines(self):
        return [
            f'*{self.time_str}*',
            f'at {self.latlng_pretty}, {self.alt:1f}m,',
            f' (facing {self.direction:.1f}°)',
        ]

    # lists

    @staticmethod
    @cache
    def image_path_list() -> list[str]:
        image_path_list = []
        for file_name in os.listdir(MetaData.DIR_IMAGES):
            ext = file_name.split('.')[-1]
            if ext not in ['jpg', 'jpeg', 'png']:
                continue
            image_path = os.path.join(MetaData.DIR_IMAGES, file_name)
            image_path_list.append(image_path)
        return image_path_list

    @staticmethod
    @cache
    def list_all():
        return [
            MetaData.from_image(img_path)
            for img_path in MetaData.image_path_list()
        ]

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
        lines = ['# Parks of Sri Lanka (Trees)', '']
        for md in MetaData.list_all():
            lines.append(f'## {md.image_path_unix}')
            lines.append('')
            lines.extend(md.description_lines)
            lines.append('')
            lines.append(f'![{md.image_path_unix}]({md.image_path_unix})')
            lines.append('')
        File(MetaData.README_PATH).write_lines(lines)
        log.debug(f'Wrote {MetaData.README_PATH}')
