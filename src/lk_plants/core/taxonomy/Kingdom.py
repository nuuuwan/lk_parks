from dataclasses import dataclass

from lk_plants.core.gbif.GBIF import GBIF
from lk_plants.core.taxonomy.Domain import Domain
from lk_plants.core.taxonomy.Taxon import Taxon


@dataclass
class Kingdom(Taxon):
    domain: Domain

    @classmethod
    def unknown(cls):
        return cls(name='unknown', domain=Domain.EUKARYOTA)
    def to_dict(self):
        return dict(
            name=self.name,
            domain_name=self.domain.name,
        )

    @staticmethod
    def from_dict(d):
        return Kingdom(
            name=d['name'], domain=Domain.EUKARYOTA
        )

    @staticmethod
    def from_species_name(species_name):
        gbif = GBIF(species_name)
        kingdom = Kingdom(
            name=gbif.data['kingdom'],
            domain=Domain.EUKARYOTA,
        )
        kingdom.write()
        return kingdom
