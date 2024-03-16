from lk_plants import NameTranslator

TEST_SCIENTIFIC_NAMES = [
    'Terminalia arjuna',
    'Mangifera indica',
    'Cocos nucifera',
    'Azadirachta indica',
    'Ficus religiosa',
]


def main():
    nt = NameTranslator()
    nt.cleanup()
    for scientific_name in TEST_SCIENTIFIC_NAMES:
        print(scientific_name, nt.get_common_names(scientific_name))


if __name__ == "__main__":
    main()
