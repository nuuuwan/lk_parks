import os
import re
from dataclasses import dataclass
from functools import cached_property

from utils import JSONFile, Log

from lk_plants.core.gbif import GBIF

log = Log('Taxon')


@dataclass
class Taxon:
    name: str
    authorship: str
    parent: 'Taxon'

    @classmethod
    def unknown(cls):
        parent_cls = cls.get_parent_class()
        parent = None
        if parent_cls is not None:
            parent = parent_cls.unknown()
        return cls(
            name='Unknown-' + cls.__name__, authorship='', parent=parent
        )

    @classmethod
    def get_class_key(cls):
        return cls.__name__.lower()

    def to_dict(self) -> dict:
        return dict(
            name=self.name,
            authorship=self.authorship,
            parent_name=self.parent.name,
        )

    @classmethod
    def from_dict(cls, d: dict) -> 'Taxon':
        parent_cls = cls.get_parent_class()

        needs_update = False
        if 'parent_name' in d:
            parent = parent_cls.from_name(d['parent_name'])
        else:
            parent_cls = cls.get_parent_class()
            parent_class_key = parent_cls.get_class_key()
            k = parent_class_key + "_name"
            needs_update = True

            if k in d:
                parent = parent_cls.from_name(d[k])
            else:
                parent = parent_cls.unknown()

        if 'authorship' in d:
            authorship = d['authorship']
        else:
            authorship = ""
            needs_update = True

        taxon = cls(
            name=d['name'],
            authorship=authorship,
            parent=parent,
        )
        if needs_update:
            taxon.write()
        return taxon
    def __hash__(self):
        return hash(self.__class__.__name__ + '.' + self.name)

    @cached_property
    def wiki_page_name(self) -> str:
        return self.name.replace(' ', '_')

    @property
    def data_path(self) -> str:
        return self.get_data_path(self.name)

    def write(self):
        if not os.path.exists(self.data_path):
            JSONFile(self.data_path).write(self.to_dict())
            log.info(f'Wrote {self.data_path}')

    @staticmethod
    def clean_name(name: str) -> str:
        name = re.sub(r'[^a-zA-Z] ', ' ', name)
        name = re.sub(r' +', ' ', name)
        return name.strip()

    @classmethod
    def get_parent_class(cls):
        raise NotImplementedError

    @classmethod
    def get_dir_data(cls) -> str:
        return os.path.join(
            'data',
            'taxonomy',
            cls.__name__.lower(),
        )

    @classmethod
    def get_data_path(cls, name: str) -> str:
        name_snake = name.replace(' ', '_').lower()
        dir_data = cls.get_dir_data()
        if not os.path.exists(dir_data):
            os.makedirs(dir_data)
        return os.path.join(dir_data, f'{name_snake}.json')

    @classmethod
    def from_name(cls, name: str):
        if name == "Eukaryota":
            return cls.SINGLETON
        if name is None:
            return cls.unknown()
        data_path = cls.get_data_path(name)
        d = JSONFile(data_path).read()
        return cls.from_dict(d)

    @classmethod
    def from_data_path(cls, data_path):
        d = JSONFile(data_path).read()
        return cls.from_dict(d)

    @classmethod
    def list_all(cls):
        dir_data = cls.get_dir_data()
        taxon_list = []
        for file_name in os.listdir(dir_data):
            if file_name.endswith('.json'):
                data_path = os.path.join(dir_data, file_name)
                taxon = cls.from_data_path(data_path)
                taxon_list.append(taxon)
        return taxon_list

    @classmethod
    def idx(cls):
        taxon_list = cls.list_all()
        idx = {}
        for taxon in taxon_list:
            idx[taxon.name] = taxon
        return idx

    @classmethod
    def from_species_name(cls, species_name):
        class_key = cls.get_class_key()
        parent_cls = cls.get_parent_class()
        
        gbif = GBIF(species_name)
        gbif_data = gbif.data
        if not gbif_data or class_key not in gbif_data:
            return cls.unknown()
        
        taxon = cls(
            name=gbif_data[class_key],
            authorship="",
            parent=parent_cls.from_species_name(species_name),
        )
        taxon.write()
        return taxon
