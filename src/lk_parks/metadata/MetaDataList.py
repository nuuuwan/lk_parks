import os
from dataclasses import dataclass
from functools import cache

from utils import JSONFile, Log

log = Log('MetaDataList')


@dataclass
class MetaDataList:

    @property
    def cmp(self) -> int:
        lat = self.latlng[0]
        return '-'.join([self.family, self.genus,
                        self.scientific_name, f'{lat:.4f}'])

    @classmethod
    @cache
    def list_all(cls):
        md_list = []
        for file_name in os.listdir(cls.DIR_DATA_METADATA):
            if file_name.endswith('.json'):
                metadata_path = os.path.join(
                    cls.DIR_DATA_METADATA, file_name
                )
                data = JSONFile(metadata_path).read()
                md = cls(**data)
                md_list.append(md)
        md_list = sorted(md_list, key=lambda md: md.cmp)
        return md_list

    @classmethod
    @cache
    def idx(cls):
        md_list = cls.list_all()
        idx = {}
        for md in md_list:
            family = md.family
            genus = md.genus
            species = md.scientific_name

            if family not in idx:
                idx[family] = {}
            if genus not in idx[family]:
                idx[family][genus] = {}
            if species not in idx[family][genus]:
                idx[family][genus][species] = []
            idx[family][genus][species].append(md)
        return idx
