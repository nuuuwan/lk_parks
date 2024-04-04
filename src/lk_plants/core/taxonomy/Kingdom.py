from dataclasses import dataclass

from lk_plants.core.gbif.GBIF import GBIF
from lk_plants.core.taxonomy.Domain import Domain
from lk_plants.core.taxonomy.Taxon import Taxon


@dataclass
class Kingdom(Taxon):
    domain: Domain

    def to_dict(self):
        return dict(
            name=self.name,
            domain_name=self.domain.name,
        )

    @staticmethod
    def from_dict(d):
        return Domain(
            name=d['name'], domain=Domain.from_name(d['domain_name'])
        )

    @staticmethod
    def from_species_name(species_name):
        gbif = GBIF(species_name)
        kingdom = Kingdom(
            name=gbif['kingdom'],
            domain=Domain.EUKARYOTA,
        )
        kingdom.write()
        return kingdom
