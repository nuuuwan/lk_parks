import os
from functools import cached_property

import pygbif
from pygbif import species as pygbif_species
from utils import JSONFile, Log

from lk_plants.core.taxonomy import Species

pygbif.caching(True)


log = Log('GBIF')


class GBIF:
    DIR_DATA_GBIF = os.path.join('data', 'gbif')

    def __init__(self, species_name):
        self.species_name = species_name

    @cached_property
    def data(self):
        if os.path.exists(self.file_path):
            return JSONFile(self.file_path).read()
        data = self.data_nocache

        os.makedirs(GBIF.DIR_DATA_GBIF, exist_ok=True)
        JSONFile(self.file_path).write(data)
        log.info(f'Wrote {self.file_path}')

        return data

    @cached_property
    def data_nocache(self):
        gbif_data = pygbif_species.name_backbone(
            name=self.species_name, rank="species", limit=1
        )

        data = dict(
            species_key=gbif_data['speciesKey'],
            scientific_name=gbif_data['scientificName'],
            canonical_name=gbif_data['canonicalName'],
            domain="Eukaryota",
            kingdom=gbif_data['kingdom'],
            phylum=gbif_data['phylum'],
            class_=gbif_data['class'],
            order=gbif_data['order'],
            family=gbif_data['family'],
            genus=gbif_data['genus'],
            species=gbif_data['species'],
        )
        assert data['canonical_name'] == self.species_name, f"{data['canonical_name']} != {self.species_name}"
        expected_genus = self.species_name.split(' ')[0]
        assert data['genus'] == expected_genus, f"{data['genus']} != {expected_genus}"
        return data

    @cached_property
    def file_path(self) -> str:
        id = self.species_name.replace(' ', '_').lower()
        return os.path.join(GBIF.DIR_DATA_GBIF, f"{id}.json")

    @staticmethod
    def build():
        species_list = Species.list_all()
        n = len(species_list)
        for i, species in enumerate(species_list):
            log.debug(f'{i+1}/{n}) {species.name}')
            try:
                GBIF(species.name).data
            except Exception as e:
                log.error(f"{species.name}: {e}")
                continue