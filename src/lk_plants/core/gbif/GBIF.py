import os
from functools import cached_property

import pygbif
from pygbif import species as pygbif_species
from utils import JSONFile, Log, Parallel

from lk_plants.core.taxonomy import Species

pygbif.caching(True)


log = Log('GBIF')


class GBIF:
    DIR_DATA_GBIF = os.path.join('data', 'gbif')
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
            name=self.species_name, rank="species", limit=1,strict=True
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
    def build():
        species_list = Species.list_all()
        n = len(species_list)
        workers = []
        for i, species in enumerate(species_list):
            def worker(i=i, species=species):
                log.debug(f'{i+1}/{n}) {species.name}')
                try:
                    GBIF(species.name).data
                except Exception as e:
                    log.error(f"{species.name}: {e}")
            workers.append(worker)
        
        Parallel.run(workers, max_threads=GBIF.MAX_THREADS)
