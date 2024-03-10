import os
import re
from dataclasses import dataclass

from utils import JSONFile, Log

log = Log('Taxon')


@dataclass
class Taxon:
    name: str
    authorship: str

    @classmethod
    def get_dir_data(cls) -> str:
        return os.path.join(
            'data',
            'taxonomy',
            cls.__name__.lower(),
        )

    @staticmethod
    def clean_name(name: str) -> str:
        name = re.sub(r'[^a-zA-Z] ', ' ', name)
        name = re.sub(r' +', ' ', name)
        return name.strip()

    @classmethod
    def get_data_path(cls, name: str) -> str:
        name_snake = name.replace(' ', '_').lower()
        dir_data = cls.get_dir_data()
        if not os.path.exists(dir_data):
            os.makedirs(dir_data)
        return os.path.join(dir_data, f'{name_snake}.json')

    @property
    def data_path(self) -> str:
        return self.get_data_path(self.name)

    def write(self):
        JSONFile(self.data_path).write(self.to_dict())
        log.info(f'Wrote {self.data_path}')

    @classmethod
    def from_name(cls, name: str):
        data_path = cls.get_data_path(name)
        d = JSONFile(data_path).read()
        return cls.from_dict(d)
