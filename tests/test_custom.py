from lk_plants import Species

species_list = Species.list_all()
species = species_list[0]
print(species)
print(species.rank_idx)
