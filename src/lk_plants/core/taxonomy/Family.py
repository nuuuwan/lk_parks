import os
from dataclasses import dataclass

from lk_plants.core.gbif import GBIF
from lk_plants.core.taxonomy.Order import Order
from lk_plants.core.taxonomy.Taxon import Taxon


@dataclass
class Family(Taxon):
    authorship: str
    order: Order

    def to_dict(self):
        return dict(
            name=self.name,
            authorship=self.authorship,
            order_name=self.order.name,
        )

    @staticmethod
    def from_dict(d):
        return Family(
            name=d['name'],
            authorship=d['authorship'],
            order=Order.from_name(d['order_name'])
            if 'order_name ' in d
            else '',
        )

    @staticmethod
    def from_plant_net_raw_result(d: dict) -> 'Family':
        d_family = d['species']['family']
        name = Taxon.clean_name(d_family['scientificNameWithoutAuthor'])
        data_path = Family.get_data_path(name)

        if os.path.exists(data_path):
            return Family.from_name(name)

        family = Family(
            name=name,
            authorship=d_family['scientificNameAuthorship'],
            order=Order.from_species_name(name),
        )
        family.write()
        return family

    @staticmethod
    def from_species_name(species_name):
        gbif = GBIF(species_name)
        family = Family(
            name=gbif.data['family'],
            authorship="",
            order=Order.from_species_name(species_name),
        )
        family.write()
        return family
