import os
from dataclasses import dataclass

from lk_parks.core.taxonomy.Family import Family
from lk_parks.core.taxonomy.Taxon import Taxon


@dataclass
class Genus(Taxon):
    family: Family

    @staticmethod
    def from_dict(d: dict) -> 'Genus':
        return Genus(
            name=d['name'],
            authorship=d['authorship'],
            family=Family.from_dict(d['family']),
        )

    @staticmethod
    def from_plantnet_result(d: dict) -> 'Genus':
        d_genus = d['species']['genus']
        name = d_genus['scientificNameWithoutAuthor']
        data_path = Genus.get_data_path(name)

        if os.path.exists(data_path):
            return Genus.from_name(name)

        family = Family.from_plantnet_result(d)
        return Genus(
            name=name,
            authorship=d_genus['scientificNameAuthorship'],
            family=family,
        )
