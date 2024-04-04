from dataclasses import dataclass

from lk_plants.core.taxonomy.Taxon import Taxon


@dataclass
class Domain(Taxon):
    def to_dict(self):
        return dict(
            name=self.name,
        )

    @staticmethod
    def from_dict(d):
        return Domain(name=d['name'])


Domain.EUKARYOTA = Domain(name='Eukaryota')
