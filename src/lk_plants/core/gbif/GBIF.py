import os
from functools import cached_property

import pygbif
from pygbif import species as pygbif_species
from utils import JSONFile, Log

pygbif.caching(True)


log = Log('GBIF')


class GBIF:
    DIR_DATA_GBIF = os.path.join('data', 'gbif')
    DIR_TAXONOMY_SPECIES = os.path.join('data', 'taxonomy', 'species')
    MAX_THREADS = 4

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
            name=self.species_name, rank="species", limit=1, strict=True
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

        observed_species = data['canonical_name']
        if observed_species != self.species_name:
            raise Exception(
                "Species name mismatch: "
                + f'"{observed_species}" != "{self.species_name}"'
            )
        expected_genus = self.species_name.split(' ')[0]
        observed_genus = data['genus']
        if data['genus'] != expected_genus:
            raise Exception(
                f'Genus mismatch: "{observed_genus}" != "{expected_genus}"'
            )
        return data

    @cached_property
    def file_path(self) -> str:
        id = self.species_name.replace(' ', '_').lower()
        return os.path.join(GBIF.DIR_DATA_GBIF, f"{id}.json")

    @staticmethod
    def get_species_name_list():
        species_name_list = []
        for file_name in os.listdir(GBIF.DIR_TAXONOMY_SPECIES):
            species_name = (
                file_name.replace('.json', '').title().replace('_', ' ')
            )
            species_name_list.append(species_name)
        return species_name_list

    @staticmethod
    def build():
        species_name_list = GBIF.get_species_name_list()
        n = len(species_name_list)

        for i, species_name in enumerate(species_name_list):
            log.debug(f'{i+1}/{n}) {species_name}')
            try:
                GBIF(species_name).data

            except Exception as e:
                log.error(f"{species_name}: {e}")
