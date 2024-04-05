
from lk_plants.core.taxonomy.Classis import Classis
from lk_plants.core.taxonomy.Taxon import Taxon


class Order(Taxon):
    @classmethod
    def get_parent_class(cls):
        return Classis
