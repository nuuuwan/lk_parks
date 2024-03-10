import os
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
            cls.name.lower(),
        )

    @classmethod
    def get_data_path(cls, name: str) -> str:
        name_snake = name.replace(' ', '_').lower()
        return os.path.join(cls.dir_data, f'{name_snake}.json')

    @property
    def data_path(self) -> str:
        return self.get_data_path(self.name)

    def write(self):
        JSONFile(self.data_path).write(self.__dict__)
        log.info(f'Wrote {self.data_path}')

    @classmethod
    def from_name(cls, name: str):
        data_path = cls.get_data_path(name)
        d = JSONFile(data_path).read()
        return cls.from_dict(d)
