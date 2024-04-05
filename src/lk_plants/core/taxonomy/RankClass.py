from lk_plants.core.taxonomy.Family import Family
from lk_plants.core.taxonomy.Genus import Genus
from lk_plants.core.taxonomy.higher import (
    Classis,
    Domain,
    Kingdom,
    Order,
    Phylum,
)
from lk_plants.core.taxonomy.Species import Species


class RankClass:
    @staticmethod
    def list_all():
        return [
            Domain,
            Kingdom,
            Phylum,
            Classis,
            Order,
            Family,
            Genus,
            Species,
        ]

    def list_all_keys():
        return [rank.get_class_key() for rank in RankClass.list_all()]
