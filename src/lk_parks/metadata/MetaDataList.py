import os
from dataclasses import dataclass
from functools import cache

from utils import JSONFile, Log

log = Log('MetaDataList')


@dataclass
class MetaDataList:

    @property
    def cmp(self) -> int:
        lat, lng = self.latlng
        return lat * 1000 + lng

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
        md_list = sorted(md_list, key=lambda md: md.cmp, reverse=True)
        return md_list

    @classmethod
    @cache
    def summary(cls) -> dict:
        md_list = cls.list_all()

        def get_key_to_n(key_lambda):
            key_to_n = {}
            for md in cls.list_all():
                key = key_lambda(md)
                if key not in key_to_n:
                    key_to_n[key] = 0
                key_to_n[key] += 1
            sorted_key_to_n = dict(
                sorted(
                    key_to_n.items(),
                    key=lambda item: item[1],
                    reverse=True))
            return sorted_key_to_n

        return dict(
            n=len(md_list),
            family_to_n=get_key_to_n(lambda md: md.family),
            genus_to_n=get_key_to_n(lambda md: f'{md.genus} ({md.family})'),
            species_to_n=get_key_to_n(lambda md: md.scientific_name),
        )
