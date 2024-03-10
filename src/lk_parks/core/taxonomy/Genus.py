import os
from dataclasses import dataclass

from lk_parks.core.taxonomy.Family import Family
from lk_parks.core.taxonomy.Taxon import Taxon


@dataclass
class Genus(Taxon):
    family: Family

    def to_dict(self) -> dict:
        return dict(
            name=self.name,
            authorship=self.authorship,
            family_name=self.family.name,
        )

    @staticmethod
    def from_dict(d: dict) -> 'Genus':
        return Genus(
            name=d['name'],
            authorship=d['authorship'],
            family=Family.from_name(d['family_name']),
        )

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
            family=family,
        )
        genus.write()
        return genus
