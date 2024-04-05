import re
from dataclasses import dataclass
from functools import cached_property

from utils import Log

from lk_plants.core.taxonomy.taxon.TaxonList import TaxonList
from lk_plants.core.taxonomy.taxon.TaxonSerialize import TaxonSerialize

log = Log('Taxon')


@dataclass
class Taxon(TaxonSerialize, TaxonList):
    name: str
    authorship: str
    parent: 'Taxon'

    @classmethod
    def unknown_name(cls):
        return 'Unknown-' + cls.__name__

    @classmethod
    def unknown(cls):
        parent_cls = cls.get_parent_class()
        parent = None
        if parent_cls is not None:
            parent = parent_cls.unknown()
        return cls(name=cls.unknown_name(), authorship='', parent=parent)

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
            taxon.write(force=True)
        return taxon

    def __hash__(self):
        return hash(self.__class__.__name__ + '.' + self.name)

    @cached_property
    def wiki_page_name(self) -> str:
        return self.name.replace(' ', '_')

    @staticmethod
    def clean_name(name: str) -> str:
        name = re.sub(r'[^a-zA-Z] ', ' ', name)
        name = re.sub(r' +', ' ', name)
        return name.strip()

    @classmethod
    def get_parent_class(cls):
        raise NotImplementedError


    @cached_property 
    def rank_names(self):
        return [self.name] + (
            self.parent.rank_names if self.parent else []
        )