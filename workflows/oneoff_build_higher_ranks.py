from utils import Log

from lk_plants import GBIF, Family

log = Log('oneoff_build_higher_ranks')


def main():
    species_name_list = GBIF.get_species_name_list()
    for species_name in species_name_list:
        try:
            Family.from_species_name(species_name)
        except BaseException:
            log.error(f'[{species_name}] No Family Found')


if __name__ == "__main__":
    main()
