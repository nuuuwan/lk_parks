import os
from dataclasses import dataclass

from lk_parks.core.taxonomy.Genus import Genus
from lk_parks.core.taxonomy.Taxon import Taxon


@dataclass
class Species(Taxon):
    genus: Genus
    gbif_id: str
    powo_id: str
    iucn_id: str
    iucn_category: str

    @property
    def family(self):
        return self.genus.family

    # static methods

    @staticmethod
    def from_dict(d):
        return Species(
            name=d['name'],
            authorship=d['authorship'],
            genus=Genus.from_dict(d['genus']),
            gbif_id=d['gbif_id'],
            powo_id=d['powo_id'],
            iucn_id=d['iucn_id'],
            iucn_category=d['iucn_category'],
        )

    @staticmethod
    def from_plantnet_result(d: dict) -> 'Species':
        d_species = d['species']
        name = d_species['scientificNameWithoutAuthor']
        data_path = Species.get_data_path(name)

        if os.path.exists(data_path):
            return Species.from_name(name)

        genus = Genus.from_plantnet_result(d)
        return Species(
            name=name,
            authorship=d_species['scientificNameAuthorship'],
            genus=genus,
            gbif_id=d_species['gbif']['id'],
            powo_id=d_species['powo']['id'],
            iucn_id=d_species['iucn']['id'],
            iucn_category=d_species['iucn']['category'],
        )
