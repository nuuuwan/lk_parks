from dataclasses import dataclass

from lk_plants.core.taxonomy.higher.Phylum import Phylum
from lk_plants.core.taxonomy.taxon.Taxon import Taxon


@dataclass
class Classis(Taxon):
    @classmethod
    def get_parent_class(cls):
        return Phylum
