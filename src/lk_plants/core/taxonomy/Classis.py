from dataclasses import dataclass

from lk_plants.core.gbif.GBIF import GBIF
from lk_plants.core.taxonomy.Phylum import Phylum
from lk_plants.core.taxonomy.Taxon import Taxon


@dataclass
class Classis(Taxon):
    phylum: Phylum

    @classmethod
    def unknown(cls):
        return cls(name='unknown-classis', phylum=Phylum.unknown())
    def to_dict(self):
        return dict(
            name=self.name,
            phylum_name=self.phylum.name,
        )

    @staticmethod
    def from_dict(d):
        return Classis(
            name=d['name'], phylum=Phylum.from_name(d['phylum_name'])
        )

    @staticmethod
    def from_species_name(species_name):
        gbif = GBIF(species_name)
        classis = Classis(
            name=gbif.data['class_'],
            phylum=Phylum.from_species_name(species_name),
        )
        classis.write()
        return classis
