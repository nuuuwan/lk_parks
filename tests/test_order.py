from lk_plants import GBIF, Order
from utils import Log 

log = Log('test_order')

def main():
    species_name_list = GBIF.get_species_name_list()
    for species_name in species_name_list:
        try:
            Order.from_species_name(species_name)
        except:
            log.error(f'[{species_name}] No Order Found')
if __name__ == "__main__":
    main()
