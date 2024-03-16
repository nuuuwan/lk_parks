import os
from dataclasses import dataclass

from lk_plants.core.misc.NameTranslator import NameTranslator
from lk_plants.core.taxonomy.Genus import Genus
from lk_plants.core.taxonomy.Taxon import Taxon


@dataclass
class Species(Taxon):
    genus: Genus
    gbif_id: str
    powo_id: str
    iucn_id: str
    iucn_category: str
    common_names: list[str]

    def __hash__(self):
        return hash(self.name)

    @property
    def family(self):
        return self.genus.family

    # static methods

    def to_dict(self) -> dict:
        return dict(
            name=self.name,
            authorship=self.authorship,
            genus_name=self.genus.name,
            family_name=self.family.name,
            gbif_id=self.gbif_id,
            powo_id=self.powo_id,
            iucn_id=self.iucn_id,
            iucn_category=self.iucn_category,
            common_names=self.common_names,
        )

    @staticmethod
    def from_dict(d):
        return Species(
            name=d['name'],
            authorship=d['authorship'],
            genus=Genus.from_name(d['genus_name']),
            gbif_id=d['gbif_id'],
            powo_id=d['powo_id'],
            iucn_id=d['iucn_id'],
            iucn_category=d['iucn_category'],
            common_names=d['common_names'],
        )

    @staticmethod
    def from_plant_net_raw_result(d: dict) -> 'Species':
        d_species = d['species']
        name = Taxon.clean_name(d_species['scientificNameWithoutAuthor'])
        data_path = Species.get_data_path(name)

        if os.path.exists(data_path):
            return Species.from_name(name)

        genus = Genus.from_plant_net_raw_result(d)

        common_names = d_species.get('commonNames', [])

        def get_attr(d, k1, k2):
            v1 = d.get(k1, {})
            if not v1:
                return None
            return v1.get(k2, None)

        common_names2 = NameTranslator().get_common_names(name)
        combined_common_names = sorted(
            list(set(common_names + common_names2))
        )

        species = Species(
            name=name,
            authorship=d_species['scientificNameAuthorship'],
            genus=genus,
            gbif_id=get_attr(d, 'gbif', 'id'),
            powo_id=get_attr(d, 'powo', 'id'),
            iucn_id=get_attr(d, 'iucn', 'id'),
            iucn_category=get_attr(d, 'iucn', 'category'),
            common_names=combined_common_names,
        )
        species.write()
        return species
