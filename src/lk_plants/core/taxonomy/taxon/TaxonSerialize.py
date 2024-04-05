import os
from dataclasses import dataclass

from utils import JSONFile, Log

from lk_plants.core.gbif import GBIF

log = Log('TaxonSerialize')


@dataclass
class TaxonSerialize:
    @property
    def data_path(self) -> str:
        return self.get_data_path(self.name)

    def write(self, force=False):
        if not os.path.exists(self.data_path) or force:
            JSONFile(self.data_path).write(self.to_dict())
            log.info(f'Wrote {self.data_path}')

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
    def from_data_path(cls, data_path):
        d = JSONFile(data_path).read()
        return cls.from_dict(d)

    @classmethod
    def from_name(cls, name: str):
        if name == "Eukaryota":
            return cls.SINGLETON
        if name is None or name == cls.unknown_name():
            return cls.unknown()
        data_path = cls.get_data_path(name)
        return cls.from_data_path(data_path)

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
