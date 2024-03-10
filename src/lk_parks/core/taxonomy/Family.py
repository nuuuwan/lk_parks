import os

from lk_parks.core.taxonomy.Taxon import Taxon


class Family(Taxon):
    def to_dict(self):
        return dict(
            name=self.name,
            authorship=self.authorship,
        )

    @staticmethod
    def from_dict(d):
        return Family(name=d['name'], authorship=d['authorship'])

    @staticmethod
    def from_plant_net_raw_result(d: dict) -> 'Family':
        d_family = d['species']['family']
        name = Taxon.clean_name(d_family['scientificNameWithoutAuthor'])
        data_path = Family.get_data_path(name)

        if os.path.exists(data_path):
            return Family.from_name(name)

        family = Family(
            name=name, authorship=d_family['scientificNameAuthorship']
        )
        family.write()
        return family
