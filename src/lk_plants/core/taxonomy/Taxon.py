import os
import re
from dataclasses import dataclass
from functools import cached_property

from utils import JSONFile, Log

log = Log('Taxon')


@dataclass
class Taxon:
    name: str

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
        if (
            not os.path.exists(self.data_path)
     
        ):
            JSONFile(self.data_path).write(self.to_dict())
            log.info(f'Wrote {self.data_path}')

    @classmethod
    def from_name(cls, name: str):
        if name is None:
            return cls.unknown()
        data_path = cls.get_data_path(name)
        d = JSONFile(data_path).read()
        return cls.from_dict(d)

    @classmethod
    def list_all(cls):
        dir_data = cls.get_dir_data()
        taxon_list = []
        for file_name in os.listdir(dir_data):
            if file_name.endswith('.json'):
                data_path = os.path.join(dir_data, file_name)
                d = JSONFile(data_path).read()
                taxon = cls.from_dict(d)
                taxon_list.append(taxon)
        return taxon_list

    @classmethod
    def idx(cls):
        taxon_list = cls.list_all()
        idx = {}
        for taxon in taxon_list:
            idx[taxon.name] = taxon
        return idx

    @cached_property
    def wiki_page_name(self) -> str:
        return self.name.replace(' ', '_')

