from lk_plants import ReadMeAbout, ReadMeFunnel, ReadMeFunnelByDay


def test_main():
    ReadMeAbout().write()
    ReadMeFunnel().write()
    ReadMeFunnelByDay().write()


if __name__ == "__main__":
    test_main()
