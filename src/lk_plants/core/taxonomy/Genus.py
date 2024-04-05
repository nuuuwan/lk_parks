import os

from lk_plants.core.taxonomy.Family import Family
from lk_plants.core.taxonomy.Taxon import Taxon


class Genus(Taxon):
    @classmethod
    def get_parent_class(cls):
        return Family

    def family(self) -> Family:
        return self.parent

    @staticmethod
    def from_plant_net_raw_result(d: dict) -> 'Genus':
        d_genus = d['species']['genus']
        name = Taxon.clean_name(d_genus['scientificNameWithoutAuthor'])
        data_path = Genus.get_data_path(name)

        if os.path.exists(data_path):
            return Genus.from_name(name)

        family = Family.from_plant_net_raw_result(d)
        genus = Genus(
            name=name,
            authorship=d_genus['scientificNameAuthorship'],
            parent=family,
        )
        genus.write()
        return genus
