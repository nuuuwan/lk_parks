import os
from dataclasses import dataclass
from functools import cache

from utils import JSONFile, Log

log = Log('MetaDataList')


@dataclass
class MetaDataList:
    SUMMARY_PATH = os.path.join('data', 'metadata.idx_summary.json')

    @property
    def cmp(self) -> int:
        p = int((1 - self.confidence) * 100 + 0.5)
        return '-'.join([self.family, self.genus,
                        self.scientific_name, f'{p:03d}'])

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

    @classmethod
    def idx_summary(cls):
        idx = cls.idx()
        idx2 = {}
        for family, family_data in idx.items():
            idx2[family] = {}
            for genus, genus_data in family_data.items():
                idx2[family][genus] = {}
                for species, md_list in genus_data.items():
                    idx2[family][genus][species] = []
                    for md in md_list:
                        idx2[family][genus][species].append(
                            md.metadata_path_unix)

        return idx2

    @classmethod
    def write_idx_summary(cls):
        idx_summary = cls.idx_summary()
        JSONFile(cls.SUMMARY_PATH).write(idx_summary)
        log.info(f'Wrote {cls.SUMMARY_PATH}')
