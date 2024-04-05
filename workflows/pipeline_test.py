from lk_plants import ReadMeSunburst, ReadMeStatisticsByTaxonomy


def test_main():
    ReadMeSunburst().write()
    ReadMeStatisticsByTaxonomy().write()


if __name__ == "__main__":
    test_main()
