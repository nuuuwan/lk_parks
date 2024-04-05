from dataclasses import dataclass

from lk_plants.core.taxonomy.Taxon import Taxon


@dataclass
class Domain(Taxon):
    @classmethod
    def get_parent_class(cls):
        return None


Domain.EUKARYOTA = Domain(name='Eukaryota', authorship="", parent=None)
Domain.SINGLETON = Domain.EUKARYOTA
