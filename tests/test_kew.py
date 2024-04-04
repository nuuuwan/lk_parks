from lk_plants import Kew


def main():
    POWO_ID = '428832-1'  # Mesua ferrea
    kew = Kew(POWO_ID)
    print(kew.classification_nocache)
    print(kew.data)


if __name__ == "__main__":
    main()
