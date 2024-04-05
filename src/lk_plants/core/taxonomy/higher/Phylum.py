from dataclasses import dataclass

from lk_plants.core.taxonomy.higher.Kingdom import Kingdom
from lk_plants.core.taxonomy.Taxon import Taxon


@dataclass
class Phylum(Taxon):
    @classmethod
    def get_parent_class(cls):
        return Kingdom
