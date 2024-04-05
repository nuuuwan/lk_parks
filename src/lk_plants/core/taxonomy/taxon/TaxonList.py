import os

from utils import Log

log = Log('TaxonList')


class TaxonList:
    @classmethod
    def list_all(cls):
        dir_data = cls.get_dir_data()
        taxon_list = []
        for file_name in os.listdir(dir_data):
            if file_name.endswith('.json'):
                data_path = os.path.join(dir_data, file_name)
                taxon = cls.from_data_path(data_path)
                taxon_list.append(taxon)
        return taxon_list

    @classmethod
    def idx(cls):
        taxon_list = cls.list_all()
        idx = {}
        for taxon in taxon_list:
            idx[taxon.name] = taxon
        return idx
