from lk_plants import GBIF, Family
from utils import Log 

log = Log('oneoff_build_higher_ranks')

def main():
    species_name_list = GBIF.get_species_name_list()
    for species_name in species_name_list:
        try:
            Family.from_species_name(species_name)
        except:
            log.error(f'[{species_name}] No Family Found')
if __name__ == "__main__":
    main()