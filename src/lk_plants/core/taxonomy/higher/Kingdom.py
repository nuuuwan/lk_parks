from dataclasses import dataclass

from lk_plants.core.taxonomy.higher.Domain import Domain
from lk_plants.core.taxonomy.Taxon import Taxon


@dataclass
class Kingdom(Taxon):
    @classmethod
    def get_parent_class(cls):
        return Domain
