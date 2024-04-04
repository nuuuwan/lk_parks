from dataclasses import dataclass

from lk_plants.core.gbif.GBIF import GBIF
from lk_plants.core.taxonomy.Classis import Classis
from lk_plants.core.taxonomy.Taxon import Taxon


@dataclass
class Order(Taxon):
    classis: Classis

    @classmethod
    def unknown(cls):
        return cls(name='unknown-order', classis=Classis.unknown())

    def to_dict(self):
        return dict(
            name=self.name,
            classis_name=self.classis.name,
        )

    @staticmethod
    def from_dict(d):
        return Order(
            name=d['name'], classis=Classis.from_name(d['classis_name'])
        )

    @staticmethod
    def from_species_name(species_name):
        gbif = GBIF(species_name)
        order = Order(
            name=gbif.data['order'],
            classis=Classis.from_species_name(species_name),
        )
        order.write()
        return order
