import os

from lk_plants.core.taxonomy.higher.Order import Order
from lk_plants.core.taxonomy.Taxon import Taxon


class Family(Taxon):
    @classmethod
    def get_parent_class(cls):
        return Order

    @staticmethod
    def from_plant_net_raw_result(d: dict) -> 'Family':
        d_family = d['species']['family']
        name = Taxon.clean_name(d_family['scientificNameWithoutAuthor'])
        data_path = Family.get_data_path(name)

        if os.path.exists(data_path):
            return Family.from_name(name)

        parent = Order.from_species_name(name)
        family = Family(
            name=name,
            authorship=d_family['scientificNameAuthorship'],
            parent=parent,
        )

        family.write()
        return family
