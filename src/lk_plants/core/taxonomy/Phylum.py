from dataclasses import dataclass

from lk_plants.core.gbif.GBIF import GBIF
from lk_plants.core.taxonomy.Kingdom import Kingdom
from lk_plants.core.taxonomy.Taxon import Taxon


@dataclass
class Phylum(Taxon):
    kingdom: Kingdom

    def to_dict(self):
        return dict(
            name=self.name,
            kingdom_name=self.kingdom.name,
        )

    @staticmethod
    def from_dict(d):
        return Kingdom(
            name=d['name'], kingdom=Kingdom.from_name(d['kingdom_name'])
        )

    @staticmethod
    def from_species_name(species_name):
        gbif = GBIF(species_name)
        phylum = Phylum(
            name=gbif.data['phylum'],
            kingdom=Kingdom.from_species_name(species_name),
        )
        phylum.write()
        return phylum
